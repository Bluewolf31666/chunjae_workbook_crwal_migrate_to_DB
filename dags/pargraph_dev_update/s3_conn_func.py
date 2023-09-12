# s3_conn_func.py
from config import ( 
    AWS_ACCESS_KEY_ID, 
    AWS_SECRET_ACCESS_KEY, 
    s3_bucket_png, 
    s3_bucket_svg
)
import os
import logging
import boto3

######### S3  UPLOAD PNG #########  
def upload_s3_png(s3, bucket, path_list, munhang_list):
    try:

        filename = os.path.basename(path_list)
        object_path  = s3_bucket_png.format(munhang_list) + filename
        s3.upload_file(path_list, bucket, object_path)
        # print("PNG Upload Success to s3 ")
            
    except Exception as e:
        logging.error(e)
        print("PNG Upload Fail to s3")
            

######### S3 UPLOAD SVG #########    
def upload_s3_svg(s3, bucket, path_list, munhang_list):
    try:

        filename = os.path.basename(path_list)
        object_path  = s3_bucket_svg.format(munhang_list) + filename
        svg_path = s3_bucket_svg.format(munhang_list) + filename

                
        s3.upload_file(path_list, bucket, object_path, ExtraArgs={"ContentType":"image/svg+xml" })

        # print("SVG Upload Success to s3")

    except Exception as e:
        logging.error(e)
        print("SVG Upload Fail to s3")
            
    return svg_path
                  
######### S3 Connection #########        
def s3_connection():
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id = AWS_ACCESS_KEY_ID,
            aws_secret_access_key = AWS_SECRET_ACCESS_KEY
            )
        # print("aws s3 Connection Success")
        return s3_client
    except:
        print("aws s3 Connection Fail ")

######### S3 이미지 URL 가져오기 #########
def get_URL(BUCKET_NAME, REGION, object_name):
    
    svg_image_url = f'https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{object_name}'
    
    
    return svg_image_url

######### platform URL #########
def get_platform_url(object_name):
    
    platform_url = f'https://img.chunjae-platform.com/{object_name}'
    
    
    return platform_url
