# Task Manager

## CI/CD (GitHub Actions)

O projeto possui pipeline completo em `.github/workflows/pipeline.yaml` com 3 estagios:

- Test: instala dependencias via Poetry e executa testes com cobertura.
- Build/Push: gera imagem Docker, publica com tags `sha-<commit>` e `latest` no Docker Hub.
- Deploy: aplica `k8s-app.yaml`, atualiza a imagem no Deployment e aguarda rollout.

### Secrets necessarios no GitHub

- `DATABASE_URL`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `KUBE_CONFIG_DATA` (kubeconfig em base64)
- `GRAFANA_ADMIN_USER` (usuario admin do Grafana)

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
