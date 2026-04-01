param location string = resourceGroup().location 

resource firewall 'Microsoft.Network/azureFirewalls@2021-05-01' = {
  name: 'sffw'
  location: location
  properties: {
    sku: {
      name: 'AZFW_VNet'
      tier: 'Basic'
    }    
    firewallPolicy: {
      id: '/subscriptions/d431bb60-5b70-4818-961a-6f4ad516eb06/resourceGroups/VM/providers/Microsoft.Network/firewallPolicies/sffwpolicy'
    }
    ipConfigurations: [
      {
        name: 'sffwpubip'
        properties: {
          subnet: {
            id: '/subscriptions/d431bb60-5b70-4818-961a-6f4ad516eb06/resourceGroups/VM/providers/Microsoft.Network/virtualNetworks/vnet-centralus/subnets/AzureFirewallSubnet'
          }
          publicIPAddress: {
            id: '/subscriptions/d431bb60-5b70-4818-961a-6f4ad516eb06/resourceGroups/VM/providers/Microsoft.Network/publicIPAddresses/sffwpubip'
          }
        }
      }
    ]
    managementIpConfiguration: {
      id: '/subscriptions/d431bb60-5b70-4818-961a-6f4ad516eb06/resourceGroups/VM/providers/Microsoft.Network/publicIPAddresses/sffwmanagement'
      name: 'sffwmanagement'
      properties: {
        publicIPAddress: {
          id: '/subscriptions/d431bb60-5b70-4818-961a-6f4ad516eb06/resourceGroups/VM/providers/Microsoft.Network/publicIPAddresses/sffwmanagement'
        }
        subnet: {
          id: '/subscriptions/d431bb60-5b70-4818-961a-6f4ad516eb06/resourceGroups/vm/providers/Microsoft.Network/virtualNetworks/vnet-centralus/subnets/AzureFirewallManagementSubnet'
        }
      }
    }
  }
}
