%w[optparse facets json date time net/http rest-client awesome_print digest/md5 uri].each { |g| require g }

SCRIPT_DIR   = (File.absolute_path(File.dirname(__FILE__))) + '/'
TOKEN_FILE   = SCRIPT_DIR + '../../token.txt'
require SCRIPT_DIR + '7br_functions.rb'
API_BASEPATH = 'https://api.sbgenomics.com/v2'

BOUNDARY = "AaB03x"

main_args = Hash.new

optparse_main = OptionParser.new do |opts|
  opts.banner = "Usage: " + File.basename(__FILE__) + " COMMAND [OPTIONS]"
  opts.separator ""
  opts.separator "Commands"
  opts.separator "   create_project: create a project."
  opts.separator "    list_projects: list all projects."
  opts.separator "          billing: query billing group."
  opts.separator "           upload: upload a list of files."
  opts.separator "   mp_upload_list: list multipart uploads."
  opts.separator "  abort_mp_upload: Abort a multipart upload."
  opts.separator "Main args:"
  opts.on('-t', '--token', "use this token (override file)") do |t|
    main_args[:token] = t
  end
  opts.separator "create_project args:"
  opts.on('-p', '--project_name STRING', "Name of project.") do |p|
  	main_args[:project_name] = p
  end
  opts.on('-d', '--description STRING', "Description of project.") do |d|
  	main_args[:description] = d
  end
  opts.separator "upload args:"
  opts.on('-f', '--files_to_upload LIST', Array, "upload files for a project.") do |d|
  	main_args[:files_to_upload] = d
  end
  opts.separator "abort_mp_upload:"
  opts.on('-u', '--upload_id LIST', Array, "upload_ids to abort") do |u|
  	main_args[:upload_id] = u
  end
end

optparse_main.parse!

if !ARGV[0]
	$stderr.puts optparse_main
	$stderr.puts
	exit
end

if main_args[:token]
	TOKEN = main_args[:token]
else
	TOKEN = File.read(TOKEN_FILE).chomp
end

if ARGV[0] == 'list_projects'
	stuff = general_get_multiple('projects')
	stuff['items'].each do |r|
		ap r
	end
elsif ARGV[0] == 'billing'
	stuff = general_get_multiple('billing/groups')
	stuff['items'].each do |r|
		ap r
	end
elsif ARGV[0] == 'create_project'
	all_project_names =get_all_project_names()
	if all_project_names.include?(main_args[:project_name])
		abort("--project_name " + main_args[:project_name] + ' already exists.')
	end
	bg = get_first_billing_group()
	create_project({billing_group:bg, name:main_args[:project_name], description:main_args[:description]})
elsif ARGV[0] == 'upload'
	p = make_project_hash()
	u = make_upload_status_hash()
	project_id = p[main_args[:project_name]]["id"]
	#initialize uploads if necessary:
	main_args[:files_to_upload].each do |file|
		next if u[File.basename(file)]
		file_size = File.size(file)
		md5 = md5_file(file)
		res = general_post({project:project_id,name:File.basename(file),size:file_size,part_size:file_size,md5:md5},'upload/multipart')
		ap res
	end
	#get upload url:
	#https://api.sbgenomics.com/v2/upload/multipart/{upload_id}/part/{part_number}
	main_args[:files_to_upload].each do |file|
		upload_id = u[File.basename(file)]['upload_id']
		res = general_get_multiple('upload/multipart/' + upload_id + '/part/1')
		#puts ('curl -X PUT ' )
		#puts("#{res}")
		#exit
		#this works:
		begin
			this_thing = RestClient.put res['url'], file
			puts("#{this_thing}")
		rescue RestClient::ExceptionWithResponse => e
			puts("DOPE!")
			puts e.response
		end 
		exit
		curl_cmd = 'curl --compressed --upload-file ' + file + ' "' + res['url'] + '"'
		curl_res = `#{curl_cmd}`
		puts(curl_res)
		#exit
		begin
			site = RestClient::Resource.new(res['url'])
			site.put File.read(file), :content_type => 'text/plain'
		rescue RestClient::ExceptionWithResponse => e
			puts e.response
		end
	end
	exit
	#complete the upload:
	main_args[:files_to_upload].each do |file|
		upload_id = u[File.basename(file)]['upload_id']
		#puts("#{file},#{upload_id}")
		 res = general_post({}, 'upload/multipart' + '/' + upload_id + '/' + 'complete')
		 #puts("#{res}")
	end
elsif ARGV[0] == 'mp_upload_list'
	stuff = general_get_multiple('upload/multipart')
	ap stuff
elsif ARGV[0] == "abort_mp_upload"
	main_args[:upload_id].each do |upload_id|
		stuff = simple_delete('upload/multipart', upload_id)
		#stuff = general_delete({upload_id:upload_id}, 'upload/multipart')
		ap stuff
	end
end
 