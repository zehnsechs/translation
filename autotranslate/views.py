import errno
import logging
import urllib

from django.http.response import HttpResponseNotFound
from django.forms.models import model_to_dict

from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from trans.models import User
from autotranslate.forms import TranslateRequestForm
from autotranslate.models import UserTranslationQuota
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.urls import reverse
from django.conf import settings
from django.db import models



import os
import requests
import datetime

from google.cloud import translate


logger = logging.getLogger(__name__)

class AutoTranslateAPI(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
            
        location = "global"
        parent = f"projects/{settings.GCLOUD_PROJECT_ID}/locations/{location}"
        
        form = TranslateRequestForm(request.POST)
        if not form.is_valid():
            logging.warning("Invalid Input")
            return JsonResponse({
                "success": False,
                "message": "Error in Translation. Contact Organizers."
            })
        text = form.cleaned_data["content"]
        input_lang = form.cleaned_data["input_lang"]
        output_lang = form.cleaned_data["output_lang"]
        if not hasattr(request.user, "usertranslationquota"):
            return JsonResponse({
                "success": False,
                "message": "No Translation Quota. Contact Organizer to Recharge."
            })
        
        updated_rows = UserTranslationQuota.objects.filter(user=request.user, credit__gte=len(text)).update(credit=models.F('credit') - len(text))
        if updated_rows == 0:
            return JsonResponse({
                "success": False,
                "message": "No Translation Quota. Contact Organizer to Recharge."
            })
        elif updated_rows > 1:
            logging.error("UNEXPECTED PART OF CODE REACHED. THIS SHOULD NOT HAPPEN.")
        try:
            client = translate.TranslationServiceClient.from_service_account_file(
                settings.GCLOUD_SERVICE_ACCOUNT_JSON_PATH)
            response = client.translate_text(
                **{
                    "parent": parent,
                    "contents": [text],
                    "mime_type": "text/plain",  # mime types: text/plain, text/html
                    "source_language_code": input_lang,
                    "target_language_code": output_lang,
                }
            )

            lines = [translation.translated_text for translation in response.translations]
            translated_text = "\n".join(lines)
            return JsonResponse({
                "success": True,
                "message": "",
                "translated_text": translated_text,
                "new_quota": UserTranslationQuota.objects.get(user=request.user).credit
            })
        except Exception as e:
            logging.error("Error in Translation. ", exc_info=e)
            return JsonResponse({
                "success": False,
                "message": "Error in Translation. Contact Organizers."
            })

