az cosmosdb sql role definition list --resource-group "rg-cxb-python-suk" --account-name "cxb-cosmos-agents-27d0shg29"

az group show --name "rg-cxb-python-suk"



az role assignment create --assignee "<your-principal-identifier>" --role "subscriptions/aaaa0a0a-bb1b-cc2c-dd3d-eeeeee4e4e4e/resourcegroups/msdocs-identity-example/providers/Microsoft.Authorization/roleDefinitions/e4e4e4e4-ffff-aaaa-bbbb-c5c5c5c5c5c5" --scope "/subscriptions/aaaa0a0a-bb1b-cc2c-dd3d-eeeeee4e4e4e/resourcegroups/msdocs-identity-example"


{
    "assignableScopes": [
        "/subscriptions/704e4a92-74df-421a-b095-447e79c88b55/resourceGroups/rg-cxb-python-suk/providers/Microsoft.DocumentDB/databaseAccounts/cxb-cosmos-agents-27d0shg29"
    ],
    "id": "/subscriptions/704e4a92-74df-421a-b095-447e79c88b55/resourceGroups/rg-cxb-python-suk/providers/Microsoft.DocumentDB/databaseAccounts/cxb-cosmos-agents-27d0shg29/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002",
    "name": "00000000-0000-0000-0000-000000000002",
    "permissions": [
        {
        "dataActions": [
            "Microsoft.DocumentDB/databaseAccounts/readMetadata",
            "Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/*",
            "Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/*"
        ],
        "notDataActions": []
        }
    ],
    "resourceGroup": "rg-cxb-python-suk",
    "roleName": "Cosmos DB Built-in Data Contributor",
    "type": "Microsoft.DocumentDB/databaseAccounts/sqlRoleDefinitions",
    "typePropertiesType": "BuiltInRole"
}


az cosmosdb show --resource-group "rg-cxb-python-suk" --name "cxb-cosmos-agents-27d0shg29" --query "{id:id}"

"id": "/subscriptions/704e4a92-74df-421a-b095-447e79c88b55/resourceGroups/rg-cxb-python-suk/providers/Microsoft.DocumentDB/databaseAccounts/cxb-cosmos-agents-27d0shg29"

az cosmosdb sql role assignment create --resource-group "rg-cxb-python-suk" --account-name "cxb-cosmos-agents-27d0shg29" --role-definition-id "/subscriptions/704e4a92-74df-421a-b095-447e79c88b55/resourceGroups/rg-cxb-python-suk/providers/Microsoft.DocumentDB/databaseAccounts/cxb-cosmos-agents-27d0shg29/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002" --principal-id "1b4d888f-e7aa-455e-b9f3-91b60076d5cc" --scope "/subscriptions/704e4a92-74df-421a-b095-447e79c88b55/resourceGroups/rg-cxb-python-suk/providers/Microsoft.DocumentDB/databaseAccounts/cxb-cosmos-agents-27d0shg29"



az cosmosdb sql role assignment list --resource-group "rg-cxb-python-suk" --account-name "cxb-cosmos-agents-27d0shg29"


webapp - b65f534b-4cba-4f1d-a7f5-fe424bc1956e

az cosmosdb sql role assignment create --resource-group "rg-cxb-python-suk" --account-name "cxb-cosmos-agents-27d0shg29" --role-definition-id "/subscriptions/704e4a92-74df-421a-b095-447e79c88b55/resourceGroups/rg-cxb-python-suk/providers/Microsoft.DocumentDB/databaseAccounts/cxb-cosmos-agents-27d0shg29/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002" --principal-id "b65f534b-4cba-4f1d-a7f5-fe424bc1956e" --scope "/subscriptions/704e4a92-74df-421a-b095-447e79c88b55/resourceGroups/rg-cxb-python-suk/providers/Microsoft.DocumentDB/databaseAccounts/cxb-cosmos-agents-27d0shg29"



```powershell

# Get the cosmos db azure resource using your resourceGroupName and accountName
$resourceGroupName = "rg-cxb-python-suk"
$accountName = "cxb-cosmos-agents-27d0shg29"
$resource = Get-AzResource -ResourceType 'Microsoft.DocumentDB/databaseAccounts' -ResourceGroupName $resourceGroupName -ResourceName $accountName

# Update property
$resource.Properties.disableLocalAuth = "False"
$resource | Set-AzResource -Force


```