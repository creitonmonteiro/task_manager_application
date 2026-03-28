variable "subscription_id" {
  description = "Azure Subscription ID"
  type        = string
}

variable "tenant_id" {
  description = "Azure Tenant ID"
  type        = string
}

variable "resource_group_name" {
  description = "Existing Resource Group where AKS will be created"
  type        = string
}

variable "location" {
  description = "Azure region for AKS resources"
  type        = string
  default     = "brazilsouth"
}

variable "cluster_name" {
  description = "AKS cluster name"
  type        = string
  default     = "aks-task-manager-staging"
}

variable "kubernetes_version" {
  description = "Optional Kubernetes version. Use null to let AKS pick default supported version"
  type        = string
  default     = null
}

variable "sku_tier" {
  description = "AKS SKU tier"
  type        = string
  default     = "Free"
}

variable "node_count" {
  description = "Number of nodes in the default node pool"
  type        = number
  default     = 2
}

variable "enable_auto_scaling" {
  description = "Enable cluster autoscaling for the default node pool"
  type        = bool
  default     = true
}

variable "node_min_count" {
  description = "Minimum number of nodes when autoscaling is enabled"
  type        = number
  default     = 2
}

variable "node_max_count" {
  description = "Maximum number of nodes when autoscaling is enabled"
  type        = number
  default     = 4
}

variable "node_vm_size" {
  description = "VM size for AKS nodes"
  type        = string
  default     = "Standard_D2as_v6"
}

variable "vnet_name" {
  description = "Name of the Virtual Network where AKS subnet will be created"
  type        = string
  default     = "vnet-aks-staging"
}

variable "vnet_address_space" {
  description = "Address space for AKS virtual network"
  type        = list(string)
  default     = ["10.40.0.0/16"]
}

variable "aks_subnet_name" {
  description = "Name of the AKS subnet"
  type        = string
  default     = "snet-aks-nodes"
}

variable "aks_subnet_prefixes" {
  description = "Address prefixes for AKS subnet"
  type        = list(string)
  default     = ["10.40.1.0/24"]
}

variable "enable_private_cluster" {
  description = "Enable private AKS API server endpoint"
  type        = bool
  default     = false
}

variable "network_plugin_mode" {
  description = "Network plugin mode for Azure CNI"
  type        = string
  default     = "overlay"
}

variable "network_policy" {
  description = "Network policy engine for AKS"
  type        = string
  default     = "azure"
}

variable "service_cidr" {
  description = "Service CIDR for Kubernetes services"
  type        = string
  default     = "10.100.0.0/16"
}

variable "dns_service_ip" {
  description = "Cluster DNS service IP"
  type        = string
  default     = "10.100.0.10"
}

variable "enable_monitoring" {
  description = "Enable Container Insights with Log Analytics"
  type        = bool
  default     = true
}

variable "log_analytics_workspace_name" {
  description = "Log Analytics workspace name used by AKS monitoring"
  type        = string
  default     = "law-aks-staging"
}

variable "log_analytics_retention_in_days" {
  description = "Retention period for Log Analytics workspace"
  type        = number
  default     = 30
}

variable "environment" {
  description = "Environment tag"
  type        = string
  default     = "staging"
}
