"""
    This file contains definitions for loading KLMS resources used in stelar_client unit tests.

"""

from stelar.client import Client

from stelar.etl import (BucketModule, Catalog, DatasetModule, FileModule, Goal,
                        OrganizationModule, ProcessModule, ResourceModule,
                        ToolModule, UserModule, VocabularyModule,
                        WorkflowModule, RelationshipModule)

c = Catalog()


stelar = c.get_package("stelar")
testing = c.get_package("stelar.testing")


stelar_klms = OrganizationModule("stelar_klms", parent=stelar, spec = {
    'name': "stelar-klms",
    'title': "Stelar KLMS",
    'description': "The Stelar Knowledge and Learning Management System",
})


red_org = OrganizationModule("red_org", testing, spec={
    'name': "red-org",
    'title': "Red Organization",
    'description': "Red is an organization for testing purposes",
})

blue_org = OrganizationModule("blue_org", testing, spec={
    'name': "blue-org",
    'title': "Blue Organization",
    'description': "Blue is an organization for testing purposes",
})


testing += VocabularyModule("daltons", tags=["joe", "jack", "william", "averell"])
klms_bucket = BucketModule("klms_bucket", spec = {
    'bucket_name': 'klms-bucket',
})
testing += klms_bucket

dataset1 = DatasetModule("dataset1", parent=testing, spec = {
    'title': "Dataset 1",
    'tags': ['test', 'dataset'],
    'notes': "A test dataset",
    'spatial': {
        "coordinates": [[[12.362, 45.39], [12.485, 45.39], [12.485, 45.576], [12.362, 45.576], [12.362, 45.39]]], 
        "type": "Polygon"
    },
})

dataset2 = DatasetModule("dataset2", parent=testing, spec = {
    'title': "Dataset 2",
    'tags': ['test', 'dataset'],
    'notes': "A 2nd test dataset",
})

dataset3 = DatasetModule("dataset3", parent=testing, spec = {
    'title': "Dataset 3",
    'tags': ['test', 'dataset'],
    'notes': "A 3rd test dataset",
})


rj_txt = FileModule("romeo_juliet", spec = {
    'bucket_name': 'klms-bucket',
    'object_name': 'rj.txt',
    'file_path': 'resources/rj.txt',
})
testing += rj_txt
rj_txt.require(klms_bucket)

shakespeare = DatasetModule("shakespeare_novels", parent=testing, spec = {
    'title': "Shakespeare Novels",
    'tags': ['another', 'novels', 'word count'],
    'notes': "A collection of several classic novels",
    'spatial': {
        "coordinates": [[[12.362, 45.39], [12.485, 45.39], [12.485, 45.576], [12.362, 45.576], [12.362, 45.39]]], 
        "type": "Polygon"
    },
})

romeo_juliet = ResourceModule(name='romeo_juliet', parent=shakespeare, spec = {
    'mime_type': 'text/plain',
    'relation': 'owned',
    'name': 'Romeo Juliet',
    'url': "s3://klms-bucket/rj.txt",
})
romeo_juliet.require(rj_txt)

simple_tool = ToolModule(name='simple_tool', parent=testing, spec = {
    "programming_language": "Python",
    "inputs": {
        "infile": "The input file"
    },
    "parameters": {
        "x": "The x parameter",
        "y": "The y parameter"
    }
})


wf1 = WorkflowModule("simple_wf", parent=testing, spec = {
    "title": "A simple workflow used in testing"
})


proc1 = ProcessModule("simple_proc", parent=testing, spec = {
    # TODO: Ideally, we would like to do the following!
    # "workflow": wf1
})
proc1.add_resource("context_resource", spec={
    "name": "Context Resource",
    "url": "s3://klms-bucket/wordcount.csv",
    "relation": "testing",
    "package_type": "process"
})

dummy2 = UserModule("dummy_user2", parent=testing, spec = {
    "username": "dummy_user2",
    "email": "dumb2@dumbville.com",
    "email_verified": True,
    "first_name": "Foo",
    "last_name": "Manchu",
    "password": "dummy_user2",
})

johndoe = UserModule("johndoe", parent=testing, spec = {
    "username": "johndoe",
    "email": "john@example.com",
    "email_verified": True,
    "first_name": "John",
    "last_name": "Doe",
    "password": "johndoe_secret",
})

janedoe = UserModule("janedoe", parent=testing, spec = {
    "username": "janedoe",
    "email": "jane@example.com",
    "email_verified": True,
    "first_name": "Jane",
    "last_name": "Doe",
    "password": "janedoe_secret",
})


#
#  Some famous datasets
#  

# Iris dataset

iris_ds = DatasetModule("iris", parent=testing, spec = {
    'title': "Iris Dataset",
    'tags': ['iris', 'flower'],
    'notes': "A classic dataset for testing",
    'spatial': {
        "coordinates": [[[12.362, 45.39], [12.485, 45.39], [12.485, 45.576], [12.362, 45.576], [12.362, 45.39]]], 
        "type": "Polygon"
    },
})
iris_csv = FileModule("iris_csv", parent=iris_ds, spec = {
    'bucket_name': 'klms-bucket',
    'object_name': 'iris.csv',
    'file_path': 'resources/iris.csv',
})
iris_csv.require(klms_bucket)
iris_ds.add_resource("iris_res", file=iris_csv, spec = {
    'mimetype': 'text/csv',
    'relation': 'owned',
    'format': 'CSV',
    'name': 'Iris Dataset CSV',
})

# The wine dataset. 

wine_ds = DatasetModule("wine", parent=testing, spec = {
    'title': "Wine Quality Dataset",
    'tags': ['wine', 'quality'],
    'notes': "A dataset containing wine quality ratings",
})
wine_csv = FileModule("wine_csv", parent=wine_ds, spec = {
    'bucket_name': 'klms-bucket',
    'object_name': 'wine_data.csv',
    'file_path': 'resources/wine_data.csv',
})
wine_csv.require(klms_bucket)
wine_ds.add_resource("wine_res", file=wine_csv, spec = {
    'mimetype': 'text/csv',
    'relation': 'owned',
    'format': 'CSV',
    'name': 'Wine Quality Dataset CSV',
})


iris_wine_link = RelationshipModule("iris_wine_link", parent=testing, spec = {
    "subject": iris_ds,
    "object": wine_ds,
    "relationship": "links_to",
    "comment": "Linking the Iris and Wine datasets for testing purposes"
})


"""
actions: 
    minio_editor: ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    
roles:
    - name: "full_minio_access"
      permissions: 
       - action: "minio_editor"
         resource: "klms-bucket/*"
       - action: "minio_editor"
         resource: "test-bucket/*"
"""


if __name__ == "__main__":
    c.client = Client('local')
    goal = Goal(c)
    goal.install(testing)
    goal.reconcile()
