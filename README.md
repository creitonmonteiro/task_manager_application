# Task Manager

## CI/CD (GitHub Actions)

O projeto possui um pipeline principal em `.github/workflows/pipeline.yaml` que orquestra workflows reutilizaveis em `.github/workflows/`.

Fluxo atual da pipeline:

- `unit_test`: instala dependencias via Poetry e executa os testes com cobertura.
- `main_build`: gera a imagem Docker e publica as tags `sha-<commit>` e `latest` no Docker Hub.
- `main_deploy`: cria/atualiza secrets, aplica manifests da aplicacao e do stack de monitoramento, atualiza a imagem do Deployment e aguarda o rollout.
- `k6_load_test`: executa o teste de carga dentro do cluster, coleta os artefatos do PVC e gera um relatorio HTML a partir do `summary.json`.

Arquivos de workflow:

- `.github/workflows/pipeline.yaml`: orquestrador principal.
- `.github/workflows/_unit_test.yml`: workflow reutilizavel de testes.
- `.github/workflows/_build.yml`: workflow reutilizavel de build e push da imagem.
- `.github/workflows/_deploy.yml`: workflow reutilizavel de deploy no Kubernetes.
- `.github/workflows/_k6.yml`: workflow reutilizavel de teste de carga e coleta de artefatos.

Comportamento por evento:

- `pull_request` para `main`: executa apenas `unit_test`, mas somente quando o PR altera arquivos que impactam a aplicacao, testes, manifests, monitoramento ou carga.
- `push` para `main`: executa `unit_test`, `main_build`, `main_deploy` e `k6_load_test`, mas somente quando o push altera arquivos que impactam a aplicacao, testes, manifests, monitoramento ou carga.
- `workflow_dispatch`: permite disparo manual da pipeline completa, inclusive para validar mudancas que nao entram no criterio automatico.

Criterio atual de execucao automatica:

- Codigo e testes: `task_manager/**`, `tests/**`, `migrations/**`.
- Carga e observabilidade: `loadtests/**`, `monitoring/**`.
- Empacotamento e execucao: `Dockerfile`, `entrypoint.sh`, `compose.yml`.
- Dependencias e configuracao da app: `pyproject.toml`, `poetry.lock`, `alembic.ini`.
- Manifests Kubernetes da aplicacao: `k8s-*.yaml`.

Exemplos de mudancas que nao disparam a pipeline automaticamente:

- documentacao em `README.md`;
- arquivos de apoio do repositorio em `.github/**`;
- infraestrutura Terraform em `infra/**`.

Relatorio de carga:

- O job `k6_load_test` publica os artefatos `k6-results/summary.json`, `k6-results/summary.html` e `k6-results/k6.log`.
- O HTML e gerado pelo script `loadtests/k6/generate-report.js`.

### Secrets necessarios no GitHub

- `DATABASE_URL`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `KUBE_CONFIG_DATA` (kubeconfig em base64)
- `GRAFANA_ADMIN_USER` (usuario admin do Grafana)

Observacoes:

- `DATABASE_URL` e usado nos testes.
- No deploy, a pipeline tambem monta internamente a connection string do Postgres do cluster para popular o secret `task-manager-secrets`.
- A senha do Grafana nao fica no GitHub: ela e gerada no primeiro deploy e persistida no secret `grafana-secrets` dentro do cluster.

## Terraform (Azure AKS)

Infra base de AKS foi adicionada em `infra/terraform` para provisionar o cluster Kubernetes.

Escopo atual de infraestrutura: somente ambiente `staging`.

### Pre-requisitos

- Service Principal com `Contributor` e `User Access Administrator` no Resource Group alvo.
- Terraform >= 1.7.

### Estrutura

- `infra/terraform/versions.tf`: versoes e providers.
- `infra/terraform/providers.tf`: provider AzureRM.
- `infra/terraform/main.tf`: recurso do cluster AKS.
- `infra/terraform/variables.tf`: parametros de ambiente.
- `infra/terraform/outputs.tf`: dados do cluster e kubeconfig.
- `infra/terraform/terraform.tfvars.example`: exemplo de valores.

O AKS e criado com:

- VNet/Subnet dedicadas para os nodes.
- Node pool `system` com autoscaling configuravel (`enable_auto_scaling`, `node_min_count`, `node_max_count`).
- Azure CNI Overlay e `network_policy` configuravel.
- Monitoramento opcional com Log Analytics (`enable_monitoring`).
- Opcao de private cluster (`enable_private_cluster`).

### Deploy

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

### Integracao com GitHub Actions

Depois do `terraform apply`, gere o valor para o secret `KUBE_CONFIG_DATA`:

```bash
terraform output -raw kube_config_data_base64
```

Salve o output no secret `KUBE_CONFIG_DATA` no GitHub.

### Observacao sobre deploy Kubernetes

Se o kubeconfig aponta para endpoint local (ex.: `https://127.0.0.1:<porta>`, comum em Minikube/Docker Desktop), o job de deploy precisa rodar em runner `self-hosted` na mesma maquina/rede do cluster. Runner hospedado do GitHub (`ubuntu-latest`) nao consegue acessar esse endpoint local.

### Como gerar KUBE_CONFIG_DATA

No seu ambiente local:

```bash
cat ~/.kube/config | base64 -w 0
```

No Windows PowerShell:

```powershell
[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes((Get-Content "$HOME/.kube/config" -Raw)))
```

Copie a saida e salve no secret `KUBE_CONFIG_DATA` do repositorio.

## Monitoring

Prometheus e Grafana podem ser aplicados no mesmo namespace com:

```bash
kubectl apply -f monitoring/prometheus.yaml
kubectl apply -f monitoring/grafana.yaml
kubectl apply -f monitoring/networkpolicy.yaml
```

Depois disso, os acessos padrao sao:

- Grafana: `http://localhost:30300`

O Prometheus fica acessivel apenas dentro do cluster (ClusterIP). Para acessar localmente para debug:

```bash
kubectl -n task-manager port-forward svc/prometheus-service 39090:9090
```

Depois abra `http://localhost:39090`.

## Load Test (k6)

Os manifests de carga ficam em `monitoring/k6-users-job.yaml` e `monitoring/k6-users-pvc.yaml`, enquanto o script de teste fica em `loadtests/k6/users-create-get.js`.

Durante a pipeline:

- o script do k6 e enviado ao cluster via ConfigMap;
- o Job `k6-users-load` grava `summary.json` e `k6.log` em um PVC;
- um pod helper temporario copia os resultados para o runner do GitHub Actions;
- o script `loadtests/k6/generate-report.js` converte o resumo JSON em HTML;
- os tres arquivos finais sao publicados como artifact do workflow.

Se precisar inspecionar os resultados manualmente no cluster, valide primeiro se o Job terminou e depois leia os arquivos montados no PVC a partir de um pod temporario.

## NetworkPolicy

As politicas em `monitoring/networkpolicy.yaml` aplicam os seguintes controles:

- Bloqueio padrao de ingress/egress para pods `prometheus` e `grafana`.
- Grafana aceita ingress somente na porta `3000`.
- Prometheus aceita ingress somente a partir do pod `grafana` na porta `9090`.
- Prometheus so pode fazer egress para `task-manager-app` (`8000`) e DNS (`53`).
- Grafana so pode fazer egress para `prometheus` (`9090`) e DNS (`53`).

Credenciais do Grafana:

- Usuario: definido pelo secret `GRAFANA_ADMIN_USER` do GitHub
- Senha: gerada automaticamente com 32 caracteres no primeiro deploy e armazenada no cluster

Para recuperar a senha:

```bash
kubectl -n task-manager get secret grafana-secrets \
  -o jsonpath='{.data.GRAFANA_ADMIN_PASSWORD}' | base64 -d
```
