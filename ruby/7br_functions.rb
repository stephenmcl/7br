def make_project_hash()
	stuff = general_get_multiple('projects')
	return_me = Hash.new
	stuff['items'].each do |s|
		return_me[s['name']] = s
	end
	return return_me
end

def md5_file(file)
	md5 = Digest::MD5.new
	File.open(file).each do |line|
		md5.update(line)
	end
	return md5.hexdigest
end

def general_post(params, api_path)
	uri = URI(API_BASEPATH + '/' + api_path)
	puts("#{params.to_json}")
	puts("#{uri}")
	res = RestClient.post uri.to_s, params.to_json, {'X-SBG-Auth-Token' => TOKEN, 'Content-Type' => 'application/json', 'Accept' => 'application/json'} #{content_type: :json, accept: :json}
	puts("#{res}")
	h = JSON.parse(res.body).to_hash if res
	return h
end

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

