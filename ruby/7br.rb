%w[optparse facets json date time net/http rest-client awesome_print digest/md5].each { |g| require g }

SCRIPT_DIR   = (File.absolute_path(File.dirname(__FILE__))) + '/'
TOKEN_FILE   = SCRIPT_DIR + '../../token.txt'
require SCRIPT_DIR + '7br_functions.rb'
API_BASEPATH = 'https://api.sbgenomics.com/v2'

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
	project_id = p[main_args[:project_name]]["id"]
	main_args[:files_to_upload].each do |file|
		file_size = File.size(file)
		md5 = md5_file(file)
		#puts("#{md5.class}")
		puts("#{file}")
		res = general_post({project:project_id,name:File.basename(file),size:file_size,part_size:file_size,md5:md5},'upload/multipart')
		#res = general_post({project:project_id,name:file},'upload/multipart')
		ap res
	end
elsif ARGV[0] == 'mp_upload_list'
	stuff = general_get_multiple('upload/multipart')
	ap stuff
end
 