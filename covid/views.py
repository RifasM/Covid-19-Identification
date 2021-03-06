import os

import numpy as np
import requests
from django.shortcuts import render
from keras.preprocessing import image

from P5_Hackathon import model_file
from P5_Hackathon.settings import MEDIA_ROOT
from covid.forms import InputForm
from covid.models import TestStatus


def home(request):
    data = requests.get("https://api.rootnet.in/covid19-in/stats").json().get("data").get("summary")
    positive = data.get("confirmedCasesIndian")
    deaths = data.get("deaths")
    discharged = data.get("discharged")

    form = InputForm()

    result = TestStatus.objects.all()

    return render(request, "index.html", {
        "form": form,
        "status": result,
        "deaths": deaths,
        "positive": positive,
        "discharged": discharged
    })


def make_prediction(request):
    if request.method == "POST":
        form = InputForm(request.POST, request.FILES)
        if form.is_valid():
            patient_name = form.cleaned_data.get("name")
            image_input_form = form.cleaned_data.get("image")

            form_file = TestStatus.objects.create(name=patient_name,
                                                  image=image_input_form,
                                                  status="")

            image_input = image.load_img(os.path.join(MEDIA_ROOT,
                                                      image_input_form.name),
                                         target_size=(300, 300))
            image_input = np.asarray(image_input)
            image_input = np.expand_dims(image_input, axis=0)

            output = model_file.predict(image_input)

            status = "Negative"

            if output[0][0] > output[0][1]:
                status = "Positive"

            TestStatus.objects.filter(id=form_file.id).update(status=status)

            result = TestStatus.objects.all()

            """model = Model(inputs=model_file.inputs, outputs=outputs)

            img = img_to_array(image_input)
            img = expand_dims(img, axis=0)
            img = preprocess_input(img)
            feature_maps = model.predict(img)

            square = 1
            for fmap in feature_maps:
                ix = 1
                for _ in range(square):
                    ax = pyplot.subplot(square, square, ix)
                    ax.set_xticks([])
                    ax.set_yticks([])
                    pyplot.imshow(fmap[0, :, :, ix - 1], cmap='gray')
                    ix += 1
                pyplot.show()"""

            result = TestStatus.objects.all()

            return render(request, "result.html", {
                "form": InputForm(),
                "status": result,
                "name": patient_name,
                "result": status
            })
