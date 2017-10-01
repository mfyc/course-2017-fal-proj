import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class request311Req(dml.Algorithm):
    contributor = 'adsouza_mcsmocha'
    reads = []
    writes = ['adsouza_mcsmocha.311Req']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('adsouza_mcsmocha', 'adsouza_mcsmocha')

        url = 'https://data.boston.gov/export/296/8e2/2968e2c0-d479-49ba-a884-4ef523ada3c0.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("311Req")
        repo.createCollection("311Req")
        repo['adsouza_mcsmocha.311Req'].insert_many(r)
        repo['adsouza_mcsmocha.311Req'].metadata({'complete':True})
        print(repo['adsouza_mcsmocha.311Req'].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}

    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('adsouza_mcsmocha', 'adsouza_mcsmocha')
       	doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        
        # Additional resource
        doc.add_namespace('anb', 'https://data.boston.gov/')

        this_script = doc.agent('alg:adsouza_mcsmocha#request311Req', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('anb:2968e2c0-d479-49ba-a884-4ef523ada3c0', {'prov:label':'311 Requests, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_311 = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_311, this_script)
        doc.usage(get_311, resource, startTime, None,
        	{prov.model.PROV_TYPE:'ont:Retrieval',
        	'ont:Query':'?type=311+Requests&$CASE_INQUIRY_ID,open_dt,target_dt,closed_dt,OnTime_Status,CASE_STATUS,CLOSURE_REASON,CASE_TITLE,SUBJECT,REASON,TYPE,QUEUE,Department,SubmittedPhoto,ClosedPhoto,Location,Fire_district,pwd_district,city_council_district,police_district,neighborhood,neighborhood_services_district,ward,precinct,LOCATION_STREET_NAME,LOCATION_ZIPCODE,Latitude,Longitude,Source'
        	}
        	)

        req_311 = doc.entity('dat:adsouza_mcsmocha#311Req', {prov.model.PROV_LABEL:'311 Requests', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(req_311, this_script)
        doc.wasGeneratedBy(req_311, get_311, endTime)
        doc.wasDerivedFrom(req_311, resource, get_311, get_311, get_311)

        repo.logout()

        return doc

 request311Req.execute()
 doc = request311Req.provenance()
 print(doc.get_provn())
 print(json.dumps(json.loads(doc.serialize()), indent=4))