%w[optparse facets json date time net/http rest-client].each { |g| require g }

SCRIPT_DIR   = (File.absolute_path(File.dirname(__FILE__))) + '/'
TOKEN_FILE   = SCRIPT_DIR + '../../token.txt'
API_BASEPATH = 'https://api.sbgenomics.com/v2'
TOKEN = File.read(TOKEN_FILE).chomp

def get_first_billing_group()
	uri = URI(API_BASEPATH + '/' + 'billing/groups')
	res = RestClient.get uri.to_s, {'X-SBG-Auth-Token' => TOKEN, 'Content-Type' => 'application/json', 'Accept' => 'application/json'}
	h = JSON.parse(res.body).to_hash if res
	return h['items'].first['id']
end

def create_project(params)
	uri = URI(API_BASEPATH + '/' + 'projects')
	#puts("#{params}")
	#exit
	puts("#{params.to_json}")
	RestClient.post uri.to_s, params.to_json, {'X-SBG-Auth-Token' => TOKEN, 'Content-Type' => 'application/json', 'Accept' => 'application/json'} #{content_type: :json, accept: :json}
	#puts("#{res}")
end

bg = get_first_billing_group()

create_project({billing_group:bg, name:"Steve_API_Demo_Project", description:"A project to demo the Seven Bridges Platform."})

exit

#list projects:
uri = URI(API_BASEPATH + '/' + 'projects')
res = RestClient.get uri.to_s, {'X-SBG-Auth-Token' => TOKEN, 'Content-Type' => 'application/json', 'Accept' => 'application/json'}

#create a new project:uri = URI(API_BASEPATH + '/' + 'projects')



