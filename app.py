from flask import Flask, render_template, request, redirect, url_for
from flask import Flask, render_template, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
from gradio_client import Client, handle_file
from gradio_client import Client, file
import shutil
import boto3
import time
import io
import secrets
import string

import requests
from PIL import Image, ImageOps
from io import BytesIO
import boto3


def generate_private_key(length=25):
    # Xác định các ký tự có thể xuất hiện trong khóa
    characters = string.ascii_letters + string.digits
    # Tạo khóa ngẫu nhiên với độ dài đã cho
    private_key = ''.join(secrets.choice(characters) for _ in range(length))
    return private_key



s3_client = boto3.client(
    's3',
    aws_access_key_id='AKIAZQ3DTG4U7QOPUJPC',
    aws_secret_access_key='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',
    region_name='us-east-1'
)
bucket_name = 'fptvton'

app = Flask(__name__)

# Dữ liệu mẫu cho sản phẩm
# Dữ liệu mẫu cho sản phẩm
products = [
    {
        'id': 1,
        'name': 'Velvet Black Bodysuit',
        'price': '250.000₫',
        'image': 'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/product/00828_00.jpg',
        'description': 'A minimalist rust-colored short-sleeve T-shirt made from soft cotton, perfect for casual outings or layering..'
    },
    {
        'id': 2,
        'name': 'Blush Contrast Polo Shirt',
        'price': '180.000₫',
        'image': 'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/product/02180_00.jpg',
        'description': ' A white short-sleeve T-shirt featuring a cheerful Minnie Mouse graphic, ideal for adding a touch of fun to your wardrobe.'
    },
    {
        'id': 3,
        'name': 'Sunshine Ribbed Henley Tee',
        'price': '160.000₫',
        'image': 'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/product/03186_00.jpg',
        'description': ' A sleek and elegant black velvet bodysuit with structured cups, designed for evening wear or formal events.'


    },
    {
        'id': 4,
        'name': 'Playful Disney Graphic Tee',
        'price': '100.000₫',
        'image': 'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/product/04743_00.jpg',
        'description': 'Mô tả chi tiết về T-shirt 4.'
    },
    {
        'id': 5,
        'name': 'Rustic Cotton T-Shirt ',
        'price': '200.000',
        'image': 'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/product/13322_00.jpg',
        'description': 'Mô tả chi tiết về T-shirt 5.'
    },
    {
        'id': 6,
        'name': 'Heather Gray Relaxed T-Shirt',
        'price': '100.000₫',
        'image': 'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/product/08759_00.jpg',
        'description': 'Mô tả chi tiết về T-shirt 6.'
    },
    {
        'id': 7,
        'name': 'Navy and Sky Polo Shirt',
        'price': '150.000₫',
        'image': 'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/product/09163_00.jpg',
        'description': 'Mô tả chi tiết về T-shirt 7.'
    },
    {
        'id': 8,
        'name': 'Ruched Crop Top with Long Sleeves',
        'price': '150.000₫',
        'image': 'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/product/10644_00.jpg',
        'description': 'Mô tả chi tiết về T-shirt 8.'
    },
]


@app.route('/')
def index():
    return render_template('index.html', products=products)



@app.route('/product/<int:product_id>',methods=['GET', 'POST'])
def product_detail(product_id):
    product = next((item for item in products if item['id'] == product_id), None)
    print(product)
    if request.method == 'POST':
        # Get the files from the form
        model_image = request.files['model_image']
        cloth_image = request.files['cloth_image']

        model_image_url = request.form.get('model_image_url')
        cloth_image_url = request.form.get('cloth_image_url')

        def process_and_upload_image(image_url, output_path, size):
            # Load the image from URL
            response = requests.get(image_url)
            response.raise_for_status()  # Raise an error for bad responses
            image = Image.open(BytesIO(response.content))
            image = ImageOps.exif_transpose(image)
            image = image.convert("RGB").resize(size)

            # Save the image to a BytesIO buffer
            image_buffer = BytesIO()
            image.save(image_buffer, format="PNG")
            image_buffer.seek(0)  # Reset buffer position

            # Upload to S3
            s3_client.upload_fileobj(image_buffer, bucket_name, output_path)
            print(f"Uploaded {output_path} successfully.")


        def process_images(model_img_path, cloth_img_path):
            key3 = generate_private_key()
            process_and_upload_image(model_img_path, f'static/upload2/{key3}/model_image_test.png', (512, 512))
            process_and_upload_image(cloth_img_path, f'static/upload2/{key3}/cloth_image_test.png', (224, 224))
            model_img_path2 = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/upload2/{key3}/model_image_test.png'
            cloth_img_path2 = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/upload2/{key3}/cloth_image_test.png'

            print(model_img_path2 )
            print(cloth_img_path2)

            from gradio_client import Client, file

            client = Client("basso4/FPT-VTON")
            result = client.predict(
                dict={"background": file(
                    model_img_path2), "layers": [],
                      "composite": None},
                garm_img=file(cloth_img_path2),
                api_name="/tryon"
            )
            print(result)

            result_img, segmentation_img = result
            return result_img, segmentation_img

        if model_image and cloth_image_url:
            key2 = generate_private_key()
            # Upload to S3
            s3_client.upload_fileobj(model_image, bucket_name, f'static/uploads/{key2}/image_model.png')
            model_image_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/uploads/{key2}/image_model.png'
            # Here you would call your model processing function to generate the output
            result_img, segmentation_img = process_images(model_image_url, cloth_image_url)

            key1 = generate_private_key()
            s3_client.upload_file(result_img, bucket_name, f'static/result/{key1}/img_result.png')
            s3_client.upload_file(segmentation_img, bucket_name, f'static/segmentation/{key1}/img_segmentation.png')

            segmentation_img_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/segmentation/{key1}/img_segmentation.png'
            result_img_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/result/{key1}/img_result.png'


            # Pass the results to the result page
            return render_template('result.html', segmentation_img_url=segmentation_img_url,
                                   result_img_url=result_img_url)


        if model_image_url and cloth_image:
            key2 = generate_private_key()
            # Upload to S3
            s3_client.upload_fileobj(cloth_image, bucket_name, f'static/uploads/{key2}/image_cloth.png')
            cloth_image_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/uploads/{key2}/image_cloth.png'
            # Here you would call your model processing function to generate the output
            result_img, segmentation_img = process_images(model_image_url, cloth_image_url)

            key1 = generate_private_key()
            s3_client.upload_file(result_img, bucket_name, f'static/result/{key1}/img_result.png')
            s3_client.upload_file(segmentation_img, bucket_name, f'static/segmentation/{key1}/img_segmentation.png')

            segmentation_img_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/segmentation/{key1}/img_segmentation.png'
            result_img_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/result/{key1}/img_result.png'


            # Pass the results to the result page
            return render_template('result.html', segmentation_img_url=segmentation_img_url,
                                   result_img_url=result_img_url)




        if model_image_url and cloth_image_url:
            result_img, segmentation_img = process_images(model_image_url, cloth_image_url)

            key1 = generate_private_key()
            s3_client.upload_file(result_img, bucket_name, f'static/result/{key1}/img_result.png')

            s3_client.upload_file(segmentation_img, bucket_name, f'static/segmentation/{key1}/img_segmentation.png')

            segmentation_img_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/segmentation/{key1}/img_segmentation.png'
            result_img_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/result/{key1}/img_result.png'


            # Pass the results to the result page
            return render_template('result.html', segmentation_img_url=segmentation_img_url,
                                   result_img_url=result_img_url)

        if model_image and cloth_image:

            key2 = generate_private_key()
            # Upload to S3
            s3_client.upload_fileobj(model_image, bucket_name, f'static/uploads/{key2}/image_model.png')
            s3_client.upload_fileobj(cloth_image, bucket_name, f'static/uploads/{key2}/image_cloth.png')
            model_image_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/uploads/{key2}/image_model.png'
            cloth_image_url =f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/uploads/{key2}/image_cloth.png'

            result_img, segmentation_img = process_images(model_image_url, cloth_image_url)

            key1 = generate_private_key()
            s3_client.upload_file(result_img, bucket_name, f'static/result/{key1}/img_result.png')

            s3_client.upload_file(segmentation_img, bucket_name, f'static/segmentation/{key1}/img_segmentation.png')

            segmentation_img_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/segmentation/{key1}/img_segmentation.png'
            result_img_url = f'https://fptvton.s3.ap-southeast-2.amazonaws.com/static/result/{key1}/img_result.png'


            # Pass the results to the result page
            return render_template('result.html', segmentation_img_url=segmentation_img_url,
                                   result_img_url=result_img_url)


    return render_template('product_detail.html', product=product)



# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True,port= 5007)