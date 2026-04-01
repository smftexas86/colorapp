param location string = resourceGroup().location

var virtualNetworkName = 'vnet-colorapp-centralus'
var subnet1Name = 'snet-pe'
var subnet2Name = 'snet-app'

resource virtualNetwork 'Microsoft.Network/virtualNetworks@2025-01-01' = {
  name: virtualNetworkName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }
  }

  resource subnet1 'subnets' = {
    name: subnet1Name
    properties: {
      addressPrefix: '10.0.0.0/24'
    }  }

  resource subnet2 'subnets' = {
    name: subnet2Name
    properties: {
      addressPrefix: '10.0.1.0/24'
    }    
  }
}

output subnet1ResourceId string = virtualNetwork::subnet1.id
output subnet2ResourceId string = virtualNetwork::subnet2.id
