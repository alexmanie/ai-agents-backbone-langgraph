from azure.cosmos import CosmosClient, PartitionKey

class CosmosDBHandler:
    def __init__(self, endpoint, key, database_name, container_name):
        self.client = CosmosClient(endpoint, key, consistency_level="Session")
        self.database = self.client.get_database_client(database_name)
        self.container = self.database.get_container_client(container_name)
        
    # def __init__(self, endpoint, credential, database_name, container_name):
    #     self.client = CosmosClient(endpoint, credential=credential, consistency_level="Session")
    #     self.database = self.client.get_database_client(database_name)
        self.container = self.database.get_container_client(container_name)

    def read_item(self, item_id, partition_key):
        try:
            item = self.container.read_item(item=item_id, partition_key=partition_key)
            return item
        except Exception as e:
            print(f"An error occurred while reading the item: {e}")
            return None

    def insert_item(self, item):
        try:
            self.container.create_item(body=item)
            print("Item inserted successfully")
        except Exception as e:
            print(f"An error occurred while inserting the item: {e}")

    def update_item(self, item_id, partition_key, updated_fields):
        try:
            item = self.container.read_item(item=item_id, partition_key=partition_key)
            for key, value in updated_fields.items():
                item[key] = value
            self.container.replace_item(item=item_id, body=item)
            print("Item updated successfully")
        except Exception as e:
            print(f"An error occurred while updating the item: {e}")

# Example usage:
# handler = CosmosDBHandler(endpoint="your_endpoint", key="your_key", database_name="your_db", container_name="your_container")
# handler.insert_item({"id": "1", "name": "John Doe", "age": 30})
# print(handler.read_item("1", "your_partition_key"))
# handler.update_item("1", "your_partition_key", {"age": 31})