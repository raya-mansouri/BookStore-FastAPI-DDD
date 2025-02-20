from sqlalchemy.orm import registry

# Create a registry object that will manage ORM mappings
mapper_registry = registry()

# Metadata object to store schema-related information such as table definitions
metadata = mapper_registry.metadata
