# https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken=CpQCAgEAAFxg8o-eU7_uKn7Yqjana-HQIx1hr5BrT4zBaEko29ANsXtp9mrqN0yrKWhf-y2PUpHRLQb1GT-mtxNcXou8TwkXhi1Jbk-ReY7oulyuvKSQrw1lgJElggGlo0d6indiH1U-tDwquw4tU_UXoQ_sj8OBo8XBUuWjuuFShqmLMP-0W59Vr6CaXdLrF8M3wFR4dUUhSf5UC4QCLaOMVP92lyh0OdtF_m_9Dt7lz-Wniod9zDrHeDsz_by570K3jL1VuDKTl_U1cJ0mzz_zDHGfOUf7VU1kVIs1WnM9SGvnm8YZURLTtMLMWx8-doGUE56Af_VfKjGDYW361OOIj9GmkyCFtaoCmTMIr5kgyeUSnB-IEhDlzujVrV6O9Mt7N4DagR6RGhT3g1viYLS4kO5YindU6dm3GIof1Q&key=YOUR_API_KEY


import requests
from laowai_panda.settings import GOOGLE_MAPS_API_KEY


#https://maps.googleapis.com/maps/api/place/details/json?placeid=ChIJsXqpTrXHhkcRNlECX-1nr10&key=AIzaSyAd3CC5hNrJA8zSl4fZbRjCGv1nlaHQR1w&language=it

def response_places(results,category):
    from placesinfo.models import Place, ErrorLog
    # print("called")
    #list
    ret = 0
    API = "https://maps.googleapis.com/maps/api/place/details/json?"
    params = {'key':GOOGLE_MAPS_API_KEY}
    for res in results:
        # print (res)
        name = res['name']
        # print(name)
        # place_id = res['place_id']
        # type = res['type']
        location = str(res['geometry']['location']['lat'])+", "+str(res['geometry']['location']['lng'])
        params['placeid']=res['place_id']
        try:
            Place.objects.get(place_id=params['placeid'])
            # print("exist")
        except:
            place_detail = requests.get(API,params=params).json()
            #get phone
            try:
                phone = place_detail['result']['international_phone_number']
                # print(phone)
            except Exception as e:
                # print ('%s (%s)' % (e, type(e)))
                ErrorLog.objects.create(error='%s (%s)' % (e, type(e)))
                phone = None
            #get site url
            try:
                site = place_detail['result']['website']
                # print(site)
            except Exception as e:
                # print ('%s (%s)' % (e, type(e)))
                ErrorLog.objects.create(error='%s (%s)' % (e, type(e)))
                site = None
            #insert in place model
            try:
                place = Place.objects.create(name=name,phone=phone,site=site,location=location)
                place.category.add(category)
                place.save()
                ret = ret +1
            except Exception as e:
                # print ('%s (%s)' % (e, type(e)))
                ErrorLog.objects.create(error='%s (%s)' % (e, type(e)))
                pass
    return ret

def get_places(query,location,radius,category):
    API = "https://maps.googleapis.com/maps/api/place/textsearch/json?key="+str(GOOGLE_MAPS_API_KEY)
    
    params = {'query': query,'location': location,'radius':radius}
    res = requests.get(API,params=params)
    ret = response_places(res.json()['results'],category)
    # print("-----------------------ret:"+str(ret))
    
    try:
        params['page_token'] = (res.json())['next_page_token']
        # print(params['page_token'])
        res1 = requests.get(API,params=params)
        ret = (response_places(res1.json()['results'],category))+ret
        # print("-----------------------ret:"+str(ret))
        try:
            # print (res1.json())
            params['page_token'] = (res1.json())['next_page_token']
            res2 = requests.get(API,params=params)
            ret =(response_places(res2.json()['results'],category))+ret
            # print("-----------------------ret:"+str(ret))
        except Exception as e:
            # print ('%s (%s)' % (e, type(e)))
            pass
    except Exception as e:
        # print ('%s (%s)' % (e, type(e)))
        
        pass
    return ret
