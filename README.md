# pyspark-recommendation-system
### My teammate on this project [Akın Bezatoğlu](https://github.com/akinbezatoglu)
Anime recommendation system with pyspark<br>
Data taken from kaggle. See:
- [MyAnimeList Dataset](https://www.kaggle.com/datasets/azathoth42/myanimelist?datasetId=28524&sortBy=voteCount)
<br>

You can skip preprocessing part and run program from Recommandaiton Engine with preprocessed data

## Contents
1. - Preprocessing
2. - Visualization
3. - Recommendation System with ALS
4. - Cosine Similarity

---

### Update : 17/03/2024
To create a S3 bucket and upload preprocessed data files the S3 bucket run the following:

```sh
$ cd sagemaker
$ python upload_data.py -n 'anime-recommendation-system' -r 'eu-central-1' -f '../preprocessed_data'

../preprocessed_data\user.csv  4579798 / 4579798.0  (100.00%)00%)
```
![uploaded-files-in-the-created-s3-bucket](https://github.com/akinbezatoglu/pyspark-recommendation-system/assets/61403011/a7da4b40-451c-4fec-aad2-576b96fbc63c)

### Create cloud infrastructure using Terraform

```sh
$ terraform init
Initializing the backend...

Initializing provider plugins...
- Finding latest version of hashicorp/aws...
- Installing hashicorp/aws v5.41.0...
- Installed hashicorp/aws v5.41.0 (signed by HashiCorp)
...
$ terraform plan
...
Plan: 4 to add, 0 to change, 0 to destroy.
$ terraform apply --auto-approve
aws_iam_policy.sagemaker_s3_full_access: Creating...
aws_iam_role.sagemaker_role: Creating...
aws_iam_policy.sagemaker_s3_full_access: Creation complete after 1s [id=arn:aws:iam::749270828329:policy/SageMaker_S3FullAccessPoliciy]
aws_iam_role.sagemaker_role: Creation complete after 1s [id=AnimeRecommendation_SageMakerRole]
aws_iam_role_policy_attachment.sagemaker_s3_policy_attachment: Creating...
aws_sagemaker_notebook_instance.notebookinstance: Creating...
aws_iam_role_policy_attachment.sagemaker_s3_policy_attachment: Creation complete after 1s [id=AnimeRecommendation_SageMakerRole-20240317120654686300000001]
aws_sagemaker_notebook_instance.notebookinstance: Still creating... [10s elapsed]
...
Apply complete! Resources: 4 added, 0 changed, 0 destroyed.
```
All resources have been created. for details, you can look at `terraform.tfstate` file.

#### Open Jupyter in the Notebook Instance that created in Amazon SageMaker

![image](https://github.com/akinbezatoglu/pyspark-recommendation-system/assets/61403011/98cd66f6-af0d-45be-a0ba-b61bad2b621d)


#### Create a new conda_python3 notebook and Run `sagemaker-anime-recommendation-system.ipynb` step by step on the Notebook Instance

You can look at the `sagemaker-anime-recommendation-system-test.html` file to see the output.

---

In this code, model data is saved locally and then uploaded properly to an s3 bucket.
```python
model.save(SparkContext.getOrCreate(), 'model')

import boto3
import os

# Initialize S3 client
s3 = boto3.client('s3')

# Upload files to the created bucket
bucketname = 'anime-recommendation-system'
local_directory = './model'
destination = 'model/'
for root, dirs, files in os.walk(local_directory):
    for filename in files:
        # construct the full local path
        local_path = os.path.join(root, filename)

        relative_path = os.path.relpath(local_path, local_directory)
        s3_path = os.path.join(destination, relative_path)
        
        s3.upload_file(local_path, bucketname, s3_path)
```
![image](https://github.com/akinbezatoglu/pyspark-recommendation-system/assets/61403011/05b111f2-f12b-408a-b1c4-adbfd377a07b)

![image](https://github.com/akinbezatoglu/pyspark-recommendation-system/assets/61403011/6a5a3dd6-2d5f-4aa1-88fb-a4469ccfc095)

---

#### Destroy the all resources
```sh
$ terraform destroy
...
Destroy complete! Resources: 4 destroyed.
```

### To load and test the model, run the `test_another_instance.ipynb` jupyter notebook

You can look at the `test_another_instance.html` file to see the output.

In this code, model data is retrieved from the s3 bucket and loaded using the Matrix Factorization Model
```python
import boto3
import os 

s3_resource = boto3.resource('s3')
bucket = s3_resource.Bucket('anime-recommendation-system') 
for obj in bucket.objects.filter(Prefix = 'model'):
    if not os.path.exists(os.path.dirname(obj.key)):
        os.makedirs(os.path.dirname(obj.key))
    bucket.download_file(obj.key, obj.key)

from pyspark import SparkContext
from pyspark.mllib.recommendation import MatrixFactorizationModel

m = MatrixFactorizationModel.load(SparkContext.getOrCreate(), 'model')
```