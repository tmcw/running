#!/usr/bin/env ruby

## disconnect

# ./disconnect.rb -u yourusername [-o /your/path] [-p yourhttpproxyserver]
#
# This is a command-line utility for the bulk-downloading of run data from
# the connect.garmin.com web application, which has lackluster export
# capabilities.
#
# Using this code is a matter of your own relationship with Garmin Connect
# and their TOS. I can't imagine this being very destructive to their service,
# and it's just filling in a hole in their existing service.
#
# It's built against Garmin Connect as of September 22, 2011. It's a scraper:
# thus if Garmin changes, this **will break**.
#
# This script requires all of the utilities on the line below: install them
# with rubygems
%w{rubygems json fileutils mechanize choice highline/import}.map{|x| require x}

LOGIN_PAGE = "https://connect.garmin.com/signin"
ACTIVITIES_SEARCH = "http://connect.garmin.com/proxy/activity-search-service-1.0/json/activities?_dc=1220170621856&start=%d"
GPX_EXPORT = "http://connect.garmin.com/proxy/activity-service-1.1/gpx/activity/%d?full=true"
KML_EXPORT = "http://connect.garmin.com/proxy/activity-service-1.0/kml/activity/%d?full=true"
TCX_EXPORT = "http://connect.garmin.com/proxy/activity-service-1.0/tcx/activity/%d?full=true"

Choice.options do
    header ''
    header 'Specific options:'

    option :user, :required => true do
        short '-u'
        long '--user=USER'
        desc 'connect.garmin.com username. Required'
    end

    option :dir do
        short '-o'
        long '--output-dir=OUTPUT'
        desc 'the directory to save .tcx files'
        default 'tcx'
    end

	option :proxy do
		short '-p'
		long '--http-proxy'
		desc 'Use HTTP proxy for remote operations'
	end
end

password = ask("Enter your password: " ) { |q| q.echo = "*" }

def login(agent, user, password)
    agent.get(LOGIN_PAGE) do |page|
	    puts "Loaded login page."
        login_form = page.form('login')
        login_form['login:loginUsernameField'] = user
        login_form['login:password'] = password

		puts "Sent login information."
        page = agent.submit(login_form, login_form.buttons.first)
        raise "Login incorrect!" if page.title().match('Sign In')
		puts "Login successful!"
        return page
	end
end

def download_run(agent, id)
    print "."
    # This downloads TCX files: you can swap out the constant, or add
    # more lines that download the different kinds of exports. I prefer TCX,
    # because despite being a 'private standard,' it includes all data,
    # including heart rate data.
    agent.get(TCX_EXPORT % (id).to_i).save_as(File.join(Choice[:dir], "%d.tcx" % id))
end

def activities(agent)
	start = 0
	while true
		j = agent.get(ACTIVITIES_SEARCH % start)
		search = JSON.parse(j.content)
		# Got some JSON content, let's see if there are any activities left to process
		if search['results']['activities']==nil then break end
		runs = search['results']['activities'].map {|r|
			# Get each activity id to insert into the download URL
			r['activity']['activityId']
		}.map {|id|
			# Download a run.
			download_run(agent, id)
			start=start+1
		}
		puts "|"
	end
end

agent = Mechanize.new

if Choice[:proxy] != nil then agent.set_proxy(Choice[:proxy], 80, nil, nil) end

# One needs to log in to get access to private runs. Mechanize will store
# the session data for the API call that cames next.
home_page = login(agent, Choice[:user], password)

FileUtils.mkdir_p(Choice[:dir]) if not File.directory?(Choice[:dir])

puts "Downloading runs..."

activities(agent)
