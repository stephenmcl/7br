%w[optparse facets json date time net/http awesome_print digest/md5 uri open3].each { |g| require g }

SCRIPT_DIR   = (File.absolute_path(File.dirname(__FILE__))) + '/'
TOKEN_FILE   = SCRIPT_DIR + '../../token.txt'
#require SCRIPT_DIR + '7br_functions.rb'
API_BASEPATH = 'https://api.sbgenomics.com/v2'

BOUNDARY = "AaB03x"
SAMTOOLS = 'samtools'

main_args = Hash.new

optparse_main = OptionParser.new do |opts|
  opts.banner = "Usage: " + File.basename(__FILE__) + " [OPTIONS]"
  opts.separator ""
  opts.on('-b', '--bam STRING', "Input BAM file to simulate.") do |t|
    main_args[:bam] = t
  end
  opts.on('-c', '--chr STRING', "Chromosome to simulate CNV on.") do |c|
  	main_args[:chr] = c
  end
  opts.on('--start STRING', "Chromosome start.") do |s|
  	main_args[:start] = s
  end
  opts.on('--stop STRING', "Chromosome stop.") do |s|
  	main_args[:stop] = s
  end
  opts.on('--cn STRING', "Copy Number to simulate.") do |c|
  	main_args[:cn] = c
  end
end

if !ARGV[0]
	$stderr.puts optparse_main
	$stderr.puts
	exit
end

optparse_main.parse!

#first, get total number of reads in the region to simulate:
cmd1 = SAMTOOLS + ' view ' + main_args[:bam] + ' ' + main_args[:chr] + ":" + main_args[:start] + "-" + main_args[:stop] + " | wc -l"

total = `#{cmd1}`
total = total.to_i

#next, get the read IDs:

cmd2 = SAMTOOLS + ' view ' + main_args[:bam] + ' ' + main_args[:chr] + ":" + main_args[:start] + "-" + main_args[:stop] + " | cut -f 1"
#puts(cmd2)
#exit
read_ids = `#{cmd2}`
read_ids = read_ids.split(/\n/)
#puts("#{read_ids}")

if main_args[:cn] == 1.to_s
	#puts("Hello!")
	#delete half the reads:
	#total = `cmd`
	reads_delete_me = Array.new
	reads_to_delete_index = (1..total.to_i).to_a.sample(total.to_i/2)
	reads_to_delete_index.each do |i|
		reads_delete_me.push(read_ids[i-1])
	end
	#puts("seriously? #{reads_delete_me.length}")
end

samtools_header_cmd = SAMTOOLS + ' view -H ' + main_args[:bam]
system(samtools_header_cmd)

samtools_view_cmd = SAMTOOLS + ' view ' + main_args[:bam] + ' ' + main_args[:chr]

Open3.popen3(samtools_view_cmd) do |stdin, stdout, stderr, wait_thr|
	while line = stdout.gets
    	line = line.chomp
    	stuff = line.split(/\t/)
    	current_read_id = stuff.first
    	if !reads_delete_me.include?(current_read_id)
    		puts(line)
    	end
  	end	
end

#puts("Total reads in region: " + total.to_s)
