# Terraform AKS Bootstrap

Este diretório provisiona o AKS para o projeto `task-manager`.

Configuracao atual: ambiente unico `staging`.

## 1) Credenciais para Terraform

Exporte as variáveis do provider AzureRM no shell usado para executar o Terraform:

```powershell
$env:ARM_CLIENT_ID       = "<appId-do-service-principal>"
$env:ARM_CLIENT_SECRET   = "<client-secret-do-service-principal>"
$env:ARM_SUBSCRIPTION_ID = "3d9cd9b4-6e93-40dd-9146-63abb8c45d15"
$env:ARM_TENANT_ID       = "334495f0-9327-40e1-9821-149fac294af5"
```

## 2) Ajustar variáveis

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
```

Atualize `terraform.tfvars` se necessario.

Principais variaveis:

- `enable_auto_scaling`: habilita autoscaling no node pool `system`.
- `node_min_count` / `node_max_count`: limites do autoscaling.
- `vnet_name`, `vnet_address_space`: rede virtual dedicada do AKS.
- `aks_subnet_name`, `aks_subnet_prefixes`: subnet dos nodes.
- `network_plugin_mode`, `network_policy`, `service_cidr`, `dns_service_ip`: ajustes de rede do cluster.
- `enable_monitoring`, `log_analytics_workspace_name`, `log_analytics_retention_in_days`: observabilidade no Azure Monitor.
- `enable_private_cluster`: endpoint privado para a API do AKS.
- `node_vm_size`: use uma SKU permitida na sua assinatura/regiao (ex.: `Standard_D2as_v6`).

## 3) Provisionar

```powershell
terraform init
terraform plan
terraform apply
```

## 4) Publicar kubeconfig no GitHub Actions

```powershell
terraform output -raw kube_config_data_base64
```

Grave a saida no secret `KUBE_CONFIG_DATA` do repositorio.

## 5) Deploy da aplicacao

O pipeline aplica os manifests em ordem:

1. `k8s-namespace.yaml`
2. `k8s-postgres.yaml`
3. `k8s-app.yaml`
4. `monitoring/*`

Com isso, o deploy consegue subir em um cluster AKS novo sem pre-criacao manual do namespace.
