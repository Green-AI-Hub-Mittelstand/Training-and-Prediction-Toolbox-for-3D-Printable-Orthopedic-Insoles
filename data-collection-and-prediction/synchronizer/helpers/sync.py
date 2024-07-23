from participants.models import *
from ..serializers import *
from django.conf import settings
import requests
import pprint
import tempfile
import json
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

pp = pprint.PrettyPrinter(indent=4)

auth_headers = {
    'Authorization': f'Token {settings.AUTH_TOKEN}',  # Assuming Token-based authentication
    'GreenAiToken': settings.GREENAI_SECRET
}

headers = {
    'Authorization': auth_headers['Authorization'],
    'GreenAiToken': settings.GREENAI_SECRET,
    'Content-Type': 'application/json',
}

def requires_true(bool, err="Did not run because decorator."):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Check if the setting is True
            if bool:
                return func(*args, **kwargs)
            else:
                print(err)
                # You can raise an exception, return a specific value, or take other actions based on your requirements.
        return wrapper
    return decorator



@requires_true(not settings.IS_REMOTE, "This should only be run on the local host")
def syncParticipant(participant_id):
    print("Snycing participant %s" % participant_id)

    localParticipant = None

    try:
        localParticipant = Participant.objects.get(pk=participant_id)
    except:
        print("Did not find local participant with id %s" % participant_id)
        return

    participants_url = f"{settings.REMOTE_HOST}/api/participants/"    
    participants = []

    # fetch all participants
    try:
        response = requests.get(participants_url, headers=headers)        
        if response.status_code == 200:
            participants = response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return

    remoteParticipant = None

    # from the remote participants, search the one that shares the public_id
    for p in participants:
        if p['public_id'] == localParticipant.public_id:
            remoteParticipant = p
            
            

    # Serialize the participant instance
    serializer = ParticipantSerializer(localParticipant)
    serialized_data = serializer.data
        

    remoteParticipantId = None

    # create or update the participant on the remote
    if remoteParticipant == None:
        print("Did not find participant, setting it up")
        
        try:
            remoteParticipant = requests.post(participants_url, json=serialized_data, headers=headers).json()
        except requests.RequestException as e:
            print(f"Request error: {e}")
            return

        try:
            remoteParticipantId = remoteParticipant['id']
        except Exception as e:
            print("Data that tried to be sent:")
            print(serialized_data)
            print()
            print(remoteParticipant)
            raise e

    else:
        # check if the remote participant is locked - if so, do not sync
        if remoteParticipant['lock_sync']:
            print("Sync lock, not syncing")
            return
        
        remoteParticipantId = remoteParticipant['id']

        try:
            remoteParticipant = requests.patch(participants_url+"%s/" % remoteParticipantId, json=serialized_data, headers=headers).json()
        except requests.RequestException as e:
                print(f"Request error: {e}")
                return

        print("Found remote participant, pushing updates")

    uploads_url = f"{settings.REMOTE_HOST}/api/uploadedfile/"  
    
    print("-------")
    print("")
    print("Uploading files... Total files locally: %s" % localParticipant.uploads.all().count() )
    print()
    # now send the files
    
    # fetch all uploads from this participants
    url = uploads_url + "?participant=%s" % remoteParticipantId
    remoteFiles = requests.get(url, headers=headers).json()
    
    
    
    for localFile in localParticipant.uploads.all():
        # check if this file exists remotely    
        
        exists = False
        
        for remoteFile in remoteFiles:
            if localFile.checksum == remoteFile['checksum']:
                exists = True
                break
        
        print("Remote file exists: %s" % exists)
        if not exists:
            # upload it
            # Serialize the participant instance
            fileSerializer = UploadedFileSerializer(localFile)
            # Access the serialized data
            serialized_data = fileSerializer.data
            
            # create the remote file
            serialized_data['participant'] = remoteParticipantId

            try:
                
                
                remoteFile = requests.post(uploads_url, headers=headers,  json=serialized_data, timeout=5).json()
            except requests.RequestException as e:
                print(f"Request error: {e}")
                return

            with open(localFile.file.path, 'rb') as file:
                file.seek(0)
                checksum = hashlib.sha256(file.read()).hexdigest()
                file.seek(0)

                print("Checksum: %s" % checksum)
                # upload the file

                headersWithContent = headers
                #headersWithContent['Content-Disposition'] = 'attachment; filename='+localFile.file.name
                #headersWithContent['Content-Type'] =  "application/octet-stream"

               
                #files = {'file': (localFile.file.name, file, 'multipart/form-data')}
                url = settings.REMOTE_HOST + "/link-file-to-uploaded-file/%s/" % remoteFile['id']

                try:
                    file_size = os.stat(localFile.file.path).st_size
                    with tqdm(total=file_size, unit="B", unit_scale=True, unit_divisor=1024) as t:
                        wrapped_file = CallbackIOWrapper(t.update, file, "read")
                        files = {'file': wrapped_file}
                        uploadResponse = requests.post(url, files=files, headers=auth_headers)
                        
                except requests.RequestException as e:
                    print(f"Request error: {e}")
                    return


                print(uploadResponse.text)
                
            
        else:
            print("File %s for paticipant %s already exists, not overwriting it" % (localFile, localParticipant.id))

        print()
        print()



@requires_true(not settings.IS_REMOTE, "This should only be run on the local host")
def syncDataprotection(data_protection_id):
    print("Snycing data protection file %s" % data_protection_id)

    localDataProtection = None

    try:
        localDataProtection = DataProtection.objects.get(pk=data_protection_id)
    except:
        print("Did not find local dataprotection  with id %s" % data_protection_id)
        return

    dataprotection_url = f"{settings.REMOTE_HOST}/api/dataprotection/"    
    dataprotections = []

    try:
        response = requests.get(dataprotection_url, headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            dataprotections = response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return

    remoteDataProtection = None

    for dp in dataprotections:
        if dp['public_id'] == localDataProtection.public_id:
            remoteDataProtection = dp

    # Serialize the localDataProtection instance
    serializer = DataProtectionSerializer(localDataProtection)
    # Access the serialized data
    serialized_data = serializer.data
        
    remoteDataProtectionId = None
    if remoteDataProtection == None:
        print("Did not find remoteDataProtection, setting it up")
        # serialize the local participant
        
        try:
            remoteDataProtection = requests.post(dataprotection_url, json=serialized_data, headers=headers).json()
        except requests.RequestException as e:
            print(f"Request error: {e}")
            return

        remoteDataProtectionId = remoteDataProtection['id']

    else:
        remoteDataProtectionId = remoteDataProtection['id']
        print("Found remote participant, pushing updates")

        try:
            remoteDataProtection = requests.patch(dataprotection_url+"%s/" % remoteDataProtectionId, json=serialized_data, headers=headers).json()
        except requests.RequestException as e:
                print(f"Request error: {e}")
                return


    if localDataProtection.pdf != None:
        try:
            with open(localDataProtection.pdf.path, 'rb') as file:
                file.seek(0)
                checksum = hashlib.sha256(file.read()).hexdigest()
                file.seek(0)

                print("Checksum: %s" % checksum)
                # upload the file

                
                files = {'file': file}
                url = settings.REMOTE_HOST + "/link-file-to-data-protection/%s/" % remoteDataProtectionId

                try:
                    uploadResponse = requests.post(url, files=files, headers=auth_headers)
                except requests.RequestException as e:
                    print(f"Request error: {e}")
                    return

                print(uploadResponse.text)
                return
        except Exception as e:
            print("Could load file: %s" % e)
    else:
        print("No PDF attached: %s" % localDataProtection)
    

from participants.models import UploadedFile

from datetime import datetime
from django.core.files import File

@requires_true(not settings.IS_REMOTE, "This should only be run on the local host")
def downloadParticipant(participant_id):
    print("Snycing participant %s" % participant_id)


    participants_url = f"{settings.REMOTE_HOST}/api/participants/?public_id={participant_id}"    
    participants = []

    # fetch the required participant by id
    try:
        response = requests.get(participants_url, headers=headers)        
        if response.status_code == 200:
            participants = response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return


    try:
        remoteParticipant = participants[0]
    except:
        print("Participant not found")
        return

    pp.pprint(remoteParticipant)

    

    
    pserializer = ParticipantSerializer(data=remoteParticipant)
    
    localParticipant = None

    if pserializer.is_valid():
        localParticipant = pserializer.save()
        
    
    print(localParticipant)
    
        

    # get system id
    participantSystemId = remoteParticipant['id']


    uploaded_files_url = f"{settings.REMOTE_HOST}/api/uploadedfile/?participant={participantSystemId}"
    uploaded_files = []

    # fetch the required participant by id
    try:
        response = requests.get(uploaded_files_url, headers=headers)        
        if response.status_code == 200:
            uploaded_files = response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return

    pp.pprint(uploaded_files)

    for f in uploaded_files:
        f['participant'] = localParticipant.id
        
        
        
        
        fSerializer = UploadedFileSerializer(data=f)

        if fSerializer.is_valid():
            localFile = fSerializer.save()

            file_url = f['file']
            print(file_url)
            

            file_name = os.path.basename(file_url)

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = f"{timestamp}_{file_name}"

            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                #temp_file.write(response.content)
                response = requests.get(file_url, stream=True, headers=auth_headers)

                # Write the content of the downloaded file to the temporary file
                with tqdm.wrapattr(open(os.devnull, "wb"), "write",  miniters=1, desc=file_name, total=int(response.headers.get('content-length', 0))) as fout:
                    for chunk in response.iter_content(chunk_size=128 * 4096):                    
                        temp_file.write(chunk)
                        fout.write(chunk)
                    
                
                #with open(temp_file.name, 'rb') as file:
                localFile.file.save(file_name, temp_file)
                localFile.writeChecksum()

            #temp_file.unlink()
            
        else:
            print(fSerializer.errors)





    # download uploads
    

