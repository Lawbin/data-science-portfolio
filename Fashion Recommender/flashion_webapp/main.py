from flask import Flask, render_template, request, redirect, url_for,send_from_directory
import pickle
import numpy as np
from PIL import Image 
import cv2
import os

#image preprocessing
import tensorflow 
from tensorflow.keras.applications import VGG19
from tensorflow.keras.applications import vgg19
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.preprocessing.image import img_to_array

#load model
from tensorflow.keras.models import load_model

app = Flask(__name__)

#define upload path and format
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['png','jpg','jpeg'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

#define attribute types
category_label = ['blazers','dresses','hoodies&sweatshirts','jackets&coats','jeans','knitwear&cardigans','pants','shorts','skirts','tops']
pattern_label = ['checks', 'dots', 'floral', 'graphic', 'solid', 'stripes']
color_label = ['black&white','blue','brown','green','light_pink&beige','orange','purple','red&pink','yellow']

#load the pre-trained model
model_for_category = tensorflow.keras.models.load_model('models/vgg19_model_category_0.60_0.96.h5')
model_for_pattern = tensorflow.keras.models.load_model('models/vgg19_model_pattern_0.54_1.00.h5')
model_for_color = tensorflow.keras.models.load_model('models/vgg19_model_color_0.64_0.95.h5')

#return link for recommendation
def getlink(category_result,pattern_result,color_result):
    category_result = category_result
    pattern_result = pattern_result
    color_result = color_result

    if category_result == 'blazers':
        Y_category_name = 'cmplt'
        Z_category_name = '5967'
    elif category_result == 'dresses':
        Y_category_name = 'vstt'
        Z_category_name = '25'
    elif category_result == 'hoodies&sweatshirts':
        Y_category_name = 'mglr'
        Z_category_name = '5968'
    elif category_result == 'jackets&coats':
        Y_category_name = 'cpspll'
        Z_category_name = '5966'
    elif category_result == 'jeans':
        Y_category_name = 'jns'
        Z_category_name = '18'
    elif category_result == 'knitwear&cardigans':
        Y_category_name = 'lngwr1'
        Z_category_name = '5969'
    elif category_result == 'pants':
        Y_category_name = 'pntln'
        Z_category_name = '417'
    elif category_result == 'shorts':
        Y_category_name = 'shrts'
        Z_category_name = '17'
    elif category_result == 'skirts':
        Y_category_name = 'gnn'
        Z_category_name = '16'
    elif category_result == 'tops':
        Y_category_name = 'tpwr'
        Z_category_name = '24'


    if pattern_result == 'checks':
        Y_pattern_name = 'chckddsg'
        Z_pattern_name = 'Checks'
    elif pattern_result == 'dots':
        Y_pattern_name = 'plkdts'
        Z_pattern_name = "Polka%20Dots"
    elif pattern_result == 'floral':
        Y_pattern_name = 'flrldsgn'
        Z_pattern_name = 'Floral'
    elif pattern_result == 'graphic':
        Y_pattern_name = 'Graphic--Logo'
        Z_pattern_name = 'Graphic'
    elif pattern_result == 'solid':
        Y_pattern_name = 'sldclr'
        Z_pattern_name = 'Solid'
    elif pattern_result == 'stripes':
        Y_pattern_name = 'strps'
        Z_pattern_name = 'Stripes'

    if color_result == 'black&white':
        Y_color_name = '6,7,25'
        Z_color_name = 'black--grey--white'
    elif color_result == 'blue':
        Y_color_name = '18'
        Z_color_name = 'blue'
    elif color_result == 'brown':
        Y_color_name = '37'
        Z_color_name = 'brown'
    elif color_result == 'green':
        Y_color_name = '22'
        Z_color_name = 'green'
    elif color_result == 'light_pink&beige':
        Y_color_name = '32,12'
        Z_color_name = 'beige'
    elif color_result == 'orange':
        Y_color_name = '9'
        Z_color_name = 'orange'
    elif color_result == 'purple':
        Y_color_name = '14'
        Z_color_name = 'purple'
    elif color_result == 'red&pink':
        Y_color_name = '11,12'
        Z_color_name = 'red--pink'
    elif color_result == 'yellow':
        Y_color_name = '10'
        Z_color_name = 'yellow'

    YOOX = "https://www.yoox.com/hk/women/shoponline/"+Y_category_name+"_mc#/dept=clothingwomen&gender=D&page=1&color="+Y_color_name+"&attributes=%7b%27ctgr%27%3a%5b%27"+Y_category_name+"%27%5d%2c%27pttrn1%27%3a%5b%27"+Y_pattern_name+"%27%5d%7d&season=X"
    ZALORA = "https://www.zalora.com.hk/women/clothing/?pattern=" + Z_pattern_name +"&color=" +Z_color_name+"&category_id="+Z_category_name

    return [YOOX,ZALORA]
    return redirect(YOOX, code=301)



#webpages
@app.route('/')
@app.route('/home')
def home():
    return render_template("index.html")

#prediction method
def prediction(img):

  img = np.array(img)
  img = cv2.resize(img,(224,224))
  img = vgg19.preprocess_input(img)
  img = np.expand_dims(img, axis=0)

  prediction_all_category = model_for_category.predict(img)
  prediction_all_pattern = model_for_pattern.predict(img)
  prediction_all_color = model_for_color.predict(img)

  final_pred_category = category_label[np.argmax(prediction_all_category)]
  final_pred_pattern = pattern_label[np.argmax(prediction_all_pattern)]
  final_pred_color = color_label[np.argmax(prediction_all_color)]

  final_prediction = {'category':final_pred_category,'pattern':final_pred_pattern,'color':final_pred_color}
  return final_prediction

#change the size of the image in proportion
def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    resized = cv2.resize(image, dim, interpolation = inter)

    return resized

def prediction_details(img):
  img_arr = np.array(img)
  img = cv2.resize(img_arr,(224,224))

  img2 = image_resize(img_arr, width = 400)
  output = img2
  img = vgg19.preprocess_input(img)
  img = np.expand_dims(img, axis=0)

  prediction_all_category = model_for_category.predict(img)
  prediction_all_pattern = model_for_pattern.predict(img)
  prediction_all_color = model_for_color.predict(img)

  # match the classes with predicted probability
  category_dict =dict(zip(category_label,prediction_all_category[0]))
  pattern_dict =dict(zip(pattern_label,prediction_all_pattern[0]))
  color_dict =dict(zip(color_label,prediction_all_color[0]))

  # sort the classes by probability
  category_dict_ordered = sorted(category_dict.items(), key=lambda kv: kv[1],reverse=True)
  pattern_dict_ordered = sorted(pattern_dict.items(), key=lambda kv: kv[1],reverse=True)
  color_dict_ordered = sorted(color_dict.items(), key=lambda kv: kv[1],reverse=True)

  # draw the predicted result on the image
  label = "{}: {:.2f}%".format(category_dict_ordered[0][0], category_dict_ordered[0][1] * 100)
  cv2.putText(output, label, (10, (0 * 30) + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 2)
  label = "{}: {:.2f}%".format(pattern_dict_ordered[0][0], pattern_dict_ordered[0][1] * 100)
  cv2.putText(output, label, (10, (1 * 30) + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 2)
  label = "{}: {:.2f}%".format(color_dict_ordered[0][0], color_dict_ordered[0][1] * 100)
  cv2.putText(output, label, (10, (2 * 30) + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 2)

  return output

@app.route('/howitworks')
def howitwork():
    return render_template("howitworks.html")

@app.route('/recommender')
def recommender():
    return render_template("recommender.html")

@app.route('/result',methods = ['GET','POST'])
def result():

    if request.method == 'POST':
        file = request.files['image_input']
        if file and allowed_file(file.filename):

            #save the uploaded file for display later
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            file_path = os.path.join(app.config['UPLOAD_FOLDER'],filename)
            print('Here is the file path')
            print(file_path)

            # Get the detailed prediction printed on the image
            img = Image.open(request.files['image_input'])
            output = prediction_details(img)
            output = Image.fromarray(output, 'RGB')
            output.save(os.path.join(app.config['UPLOAD_FOLDER'],'prediction_' + filename))
            file_path_prediction = os.path.join(app.config['UPLOAD_FOLDER'],'prediction_' + filename)
            print('Here is the file path with prediciton')
            print(file_path_prediction)

            # Simple prediction
            img = Image.open(request.files['image_input'])
            pred = prediction(img)

            print('Here is the prediction')
            print(pred)

            YOOX_link = getlink(pred['category'],pred['pattern'],pred['color'])[0]
            ZALORA_link = getlink(pred['category'],pred['pattern'],pred['color'])[1]

            print(YOOX_link)
            print(ZALORA_link)

            return render_template('result.html',file_path_prediction=file_path_prediction,file_path = file_path,YOOX_link=YOOX_link,ZALORA_link=ZALORA_link)
    else:
        return redirect(url_for('recommender'))

if __name__ == "__main__":
    app.run(debug=True)
