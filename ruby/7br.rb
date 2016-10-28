%w[optparse facets json date time net/http rest-client awesome_print].each { |g| require g }

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
end