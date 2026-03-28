locals {
  common_tags = {
    project     = "fastapi-zero"
    environment = var.environment
    managed_by  = "terraform"
  }
}

data "azurerm_resource_group" "rg" {
  name = var.resource_group_name
}

resource "azurerm_virtual_network" "aks" {
  name                = var.vnet_name
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  address_space       = var.vnet_address_space

  tags = local.common_tags
}

resource "azurerm_subnet" "aks_nodes" {
  name                 = var.aks_subnet_name
  resource_group_name  = data.azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.aks.name
  address_prefixes     = var.aks_subnet_prefixes
}

resource "azurerm_log_analytics_workspace" "aks" {
  count = var.enable_monitoring ? 1 : 0

  name                = var.log_analytics_workspace_name
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = var.log_analytics_retention_in_days

  tags = local.common_tags
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                    = var.cluster_name
  location                = data.azurerm_resource_group.rg.location
  resource_group_name     = data.azurerm_resource_group.rg.name
  dns_prefix              = "${var.cluster_name}-dns"
  sku_tier                = var.sku_tier
  private_cluster_enabled = var.enable_private_cluster

  kubernetes_version = var.kubernetes_version

  default_node_pool {
    name                 = "system"
    node_count           = var.enable_auto_scaling ? null : var.node_count
    min_count            = var.enable_auto_scaling ? var.node_min_count : null
    max_count            = var.enable_auto_scaling ? var.node_max_count : null
    vm_size              = var.node_vm_size
    os_disk_size_gb      = 64
    auto_scaling_enabled = var.enable_auto_scaling
    vnet_subnet_id       = azurerm_subnet.aks_nodes.id
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin      = "azure"
    network_plugin_mode = var.network_plugin_mode
    network_policy      = var.network_policy
    service_cidr        = var.service_cidr
    dns_service_ip      = var.dns_service_ip
    load_balancer_sku   = "standard"
  }

  dynamic "oms_agent" {
    for_each = var.enable_monitoring ? [1] : []
    content {
      log_analytics_workspace_id = azurerm_log_analytics_workspace.aks[0].id
    }
  }

  role_based_access_control_enabled = true

  tags = local.common_tags
}
