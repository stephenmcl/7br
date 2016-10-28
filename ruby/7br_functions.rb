def get_first_billing_group()
	uri = URI(API_BASEPATH + '/' + 'billing/groups')
	res = RestClient.get uri.to_s, {'X-SBG-Auth-Token' => TOKEN, 'Content-Type' => 'application/json', 'Accept' => 'application/json'}
	h = JSON.parse(res.body).to_hash if res
	return h['items'].first['id']
end

def general_get_multiple(path)
	uri = URI(API_BASEPATH + '/' + path)
	res = RestClient.get uri.to_s, {'X-SBG-Auth-Token' => TOKEN, 'Content-Type' => 'application/json', 'Accept' => 'application/json'}
	h = JSON.parse(res.body).to_hash if res
	#return h['items'].first['id']
	return h
end

def get_all_project_names()
	stuff = general_get_multiple('projects')
	return_me = Array.new
	stuff['items'].each do |r|
		return_me.push(r['name'])
	end
	return return_me
end

def create_project(params)
	uri = URI(API_BASEPATH + '/' + 'projects')
	#puts("#{params}")
	#exit
	puts("#{params.to_json}")
	RestClient.post uri.to_s, params.to_json, {'X-SBG-Auth-Token' => TOKEN, 'Content-Type' => 'application/json', 'Accept' => 'application/json'} #{content_type: :json, accept: :json}
end

