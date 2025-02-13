#
# Copyright 2015-2021, Institute for Systems Biology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import json, string, os
import requests, logging


# import TCIABrowserLib

#
# Refer https://wiki.cancerimagingarchive.net/display/Public/REST+API+Usage+Guide for complete list of API
#
class IDCClient:
    GET_IMAGE = "getImage"
    GET_MANUFACTURER_VALUES = "getManufacturerValues"
    GET_MODALITY_VALUES = "getModalityValues"
    GET_COLLECTION_VALUES = "getCollectionValues"
    GET_BODY_PART_VALUES = "getBodyPartValues"
    GET_PATIENT_STUDY = "getPatientStudy"
    GET_SERIES = "getSeries"
    GET_SERIES_SIZE = "getSeriesSize"
    GET_PATIENT = "getPatient"

    # use Slicer API key by default
    def __init__(self, baseUrl='https://dev-api.canceridc.dev/v2'): # v2 dev
    # def __init__(self, baseUrl='https://dev-api.canceridc.dev/v1'): # v1 dev
    # def __init__(self, baseUrl='http://localhost:8095/v2'):  # v2 local
        self.baseUrl = baseUrl
        self.s5cmdPath = ''

    def execute_get(self, url, params=None, json=None):

        response = requests.get(url, params=params, json=json)
        if response.status_code != 200:
            # Print the error code and message if something went wrong
            print('Request failed: {}'.format(response.reason))

        return response

    def execute_post(self, url, params=None, json=None):

        response = requests.post(url, params=params, json=json)
        if response.status_code != 200:
            # Print the error code and message if something went wrong
            print('Request failed: {}'.format(response.reason))

        return response

    def get_modality_values(self, collection=None, bodyPartExamined=None, modality=None, outputFormat="json"):
        serviceUrl = self.baseUrl + "/" + self.GET_MODALITY_VALUES
        queryParameters = {"Collection": collection, "BodyPartExamined": bodyPartExamined, "Modality": modality,
                           "format": outputFormat}
        resp = self.execute(serviceUrl, queryParameters)
        return resp

    def get_manufacturer_values(self, collection=None, bodyPartExamined=None, modality=None, outputFormat="json"):
        '''
        serviceUrl = self.baseUrl + "/" + self.GET_MANUFACTURER_VALUES
        queryParameters = {"Collection" : collection , "BodyPartExamined" : bodyPartExamined , "Modality" : modality , "format" : outputFormat }
        resp = self.execute(serviceUrl , queryParameters)
        '''
        return None

    def get_collection_values(self, outputFormat="json"):
        url = '{}/collections'.format(self.baseUrl)
        resp = self.execute_get(url)

        idc_collections = []

        for c in resp.json()['collections']:
            idc_collections.append({"Collection": c["collection_id"]})

        logging.debug("Get collections response: %s", json.dumps(idc_collections))
        return json.dumps(idc_collections)

    def get_body_part_values(self, collection=None, bodyPartExamined=None, modality=None, outputFormat="csv"):
        return None
        serviceUrl = self.baseUrl + "/" + self.GET_BODY_PART_VALUES
        queryParameters = {"Collection": collection, "BodyPartExamined": bodyPartExamined, "Modality": modality,
                           "format": outputFormat}
        resp = self.execute(serviceUrl, queryParameters)
        return resp

    '''
    def get_patient_study(self,collection = None , patientId = None , studyInstanceUid = None , outputFormat = "json" ):
        return None
        serviceUrl = self.baseUrl + "/" + self.GET_PATIENT_STUDY
        queryParameters = {"Collection" : collection , "PatientID" : patientId , "StudyInstanceUID" : studyInstanceUid , "format" : outputFormat }
        resp = self.execute(serviceUrl , queryParameters)
        return resp


    def get_series(self,collection = None , patientId = None , studyInstanceUID = None, modality = None , outputFormat = "json" ):
        return None
        serviceUrl = self.baseUrl + "/" + self.GET_SERIES
        queryParameters = {"Collection" : collection , "PatientID" : patientId ,"StudyInstanceUID": studyInstanceUID, "Modality" : modality , "format" : outputFormat }
        resp = self.execute(serviceUrl , queryParameters)
        return resp
    '''

    def get_series_size(self, seriesInstanceUid):
        return None
        serviceUrl = self.baseUrl + "/" + self.GET_SERIES_SIZE
        queryParameters = {"SeriesInstanceUID": seriesInstanceUid}
        resp = self.execute(serviceUrl, queryParameters)
        return resp

    def get_patient(self, collection=None, outputFormat="json"):
        filters = {
            "collection_id": [collection],
        }
        cohortSpec = {"name": "testcohort",
                      "description": "Test description",
                      "filters": filters}
        params = dict(
            sql=False,
            page_size=2000
        )

        fields = [
            'Collection_ID',
            'PatientID',
            'counts',
            'sizes'
            ]

        queryPreviewBody = {"cohort_def": cohortSpec,
                            "fields": fields}

        url = '{}/cohorts/query/preview'.format(self.baseUrl)
        resp = self.execute_post(url, params=params, json=queryPreviewBody)

        # print(resp.json())

        idc_json = resp.json()['query_results']['json']

        idc_response = []
        for idc_item in idc_json:
            # print(idc_item)
            idc_item = {"PatientID": idc_item['PatientID'],
                        'PatientName': '',
                        'PatientSex': '',
                        'Collection': collection,
                        'PatientAge': '',
                        'patient_size_MB': idc_item['patient_size_MB'],
                        'study_count': idc_item['study_count'],
                        'series count': idc_item['series_count'],
                        'instance_count': idc_item['instance_count']
                        }
            idc_response.append(idc_item)

        logging.debug("Get patient response: %s", json.dumps(idc_response, indent=2))

        return json.dumps(idc_response)

    def get_patient_study(self, collection=None, patientId=None, studyInstanceUid=None, outputFormat="json"):

        filters = {
            "PatientID": [patientId],
        }
        cohortSpec = {"name": "testcohort",
                      "description": "Test description",
                      "filters": filters}
        params = dict(
            sql=False,
            page_size=2000
        )

        fields = [
            'Collection_ID',
            'PatientID',
            'StudyInstanceUID',
            'StudyDate',
            'StudyDescription',
            'counts',
            'sizes'
            ]

        queryPreviewBody = {"cohort_def": cohortSpec,
                            "fields": fields}

        # url = '{}/cohorts/manifest/preview'.format(self.baseUrl)
        url = '{}/cohorts/query/preview'.format(self.baseUrl)
        resp = self.execute_post(url, params=params, json=queryPreviewBody)

        idc_json = resp.json()['query_results']['json']

        idc_response = []
        for idc_item in idc_json:
            idc_item = {'Collection': idc_item['collection_id'], \
                        'Patient_ID': patientId, \
                        'PatientName': '', \
                        'PatientSex': '', \
                        'StudyInstanceUID': idc_item['StudyInstanceUID'], \
                        'StudyDate': idc_item['StudyDate'], \
                        'StudyDescription': idc_item['StudyDescription'], \
                        'PatientAge': '', \
                        'study_size_MB': idc_item['study_size_MB'],
                        'series count': idc_item['series_count'], \
                        'instance_count': idc_item['instance_count']
                        }
            idc_response.append(idc_item)

        logging.debug("Get study response: %s", json.dumps(idc_response, indent=2))

        return json.dumps(idc_response)

    def get_series(self, collection=None, patientId=None, studyInstanceUID=None, modality=None, outputFormat="json"):
        filters = {
            "StudyInstanceUID": [studyInstanceUID],
        }
        cohortSpec = {"name": "testcohort",
                      "description": "Test description",
                      "filters": filters}
        params = dict(
            sql=False,
             page_size=2000
        )

        fields = [
            "SeriesInstanceUID",
            "Modality",
            "SeriesDescription",
            "SeriesNumber",
            "collection_id",
            "Manufacturer",
            "ManufacturerModelName",
            "sizes",
            "counts"
        ]

        queryPreviewBody = {"cohort_def": cohortSpec,
                            "fields": fields}

        # url = '{}/cohorts/manifest/preview'.format(self.baseUrl)
        url = '{}/cohorts/query/preview'.format(self.baseUrl)
        resp = self.execute_post(url, params=params, json=queryPreviewBody)

        idc_json = resp.json()['query_results']['json']

        idc_response = []
        for idc_item in idc_json:
            idc_item = {'SeriesInstanceUID': idc_item['SeriesInstanceUID'], \
                        'StudyInstanceUID': studyInstanceUID, \
                        'Modality': idc_item['Modality'], \
                        'SeriesDate': '', \
                        'SeriesDescription': idc_item['SeriesDescription'], \
                        'SeriesNumber': idc_item['SeriesNumber'], \
                        'Collection': idc_item['collection_id'], # v1 \
                        # 'Collection': idc_item['collection_id'], #  v2 \
                        'Manufacturer': idc_item['Manufacturer'], \
                        'ManufacturerModelName': idc_item['ManufacturerModelName'], \
                        'SoftwareVersions': '', \
                        'Visibility': '1', \
                        'ImageCount': '1', \
                        'series_size_MB': idc_item['series_size_MB'], \
                        'instance_count': idc_item['instance_count']
                        }
            idc_response.append(idc_item)
        logging.debug("Get series response: %s", json.dumps(idc_response, indent=2))
        return json.dumps(idc_response)

    def get_image(self, seriesInstanceUid, downloadDir, download=True):
        filters = {
            "SeriesInstanceUID": [seriesInstanceUid],
        }
        cohortSpec = {"name": "testcohort",
                      "description": "Test description",
                      "filters": filters}
        # params = dict(
        #     sql=False,
        #     Collection_ID=False,
        #     Patient_ID=False, # v1
        #     # PatientID=False, # v2
        #     StudyInstanceUID=False,
        #     SeriesInstanceUID=True,
        #     GCS_URL=True,
        #     page_size=1
        # )
        params = dict(
            sql=False,
            crdc_series_uuid=True,
            gcs_bucket=True,
            page_size=1
        )
        url = '{}/cohorts/manifest/preview'.format(self.baseUrl)
        resp = self.execute_post(url, params=params, json=cohortSpec)

        # gcs_url = resp.json()['manifest']['json_manifest'][0]['GCS_URL']
        #
        # series_url = 's3' + gcs_url[2:gcs_url.rfind('/') + 1] + '*'

        row = resp.json()['manifest']['json_manifest'][0]
        series_url = f"gs://{row['gcs_bucket']}/{row['crdc_series_uuid']}/*"

        # if not self.iss5cmdPathValid():
        #    self.setups5cmd()

        import subprocess

        cmd = [self.s5cmdPath, '--no-sign-request', '--endpoint-url', 'https://storage.googleapis.com', 'cp',
               series_url, downloadDir]
        logging.debug(" ".join(cmd))

        if download:
            ret = subprocess.run(cmd)

        return 0
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    client = IDCClient()
    r = client.get_image('1.3.6.1.4.1.14519.5.2.1.6834.5010.130448511786154037246331774347', '.', download=False)
    r = client.get_patient(collection='4d_lung', outputFormat="json")
    r = client.get_patient_study( collection='4d_lung', patientId='108_HM10395', studyInstanceUid='1.3.6.1.4.1.14519.5.2.1.6834.5010.185173640297170335553556115001', outputFormat="json")
    r = client.get_series(collection='4d_lung', patientId='108_HM10395', studyInstanceUID='1.3.6.1.4.1.14519.5.2.1.6834.5010.185173640297170335553556115001', modality=None, outputFormat="json")
