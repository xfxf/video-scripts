require 'nokogiri'
require 'net/http'
require 'date'

rooms = (1..6).to_a
rframes = []
rclients = []

rooms.each do |r|
        rframes[r] = 0
        rclients[r] = 0
end

while true do

rooms.each do |r|
        dns = "rtmp-ingest-relay-r#{r}.aws"
        doc = Nokogiri::XML(Net::HTTP.get(dns,'/room-stat'))
        clients = doc.xpath("//live/nclients[1]").text.to_i
        dframes = doc.xpath("//client[not(recording)]/dropped").text.to_i

        if rclients[r] != clients
                puts "[#{DateTime.now}] Room #{r} Client count changed, was #{rclients[r]} now #{clients}"
                rclients[r] = clients
        end
        if clients == 0
                next
        end
        if rframes[r] != dframes
                puts "[#{DateTime.now}] Room #{r} Dropped Frames count changed, was #{rframes[r]} now #{dframes}"
                if rframes[r] > dframes
                        puts "[#{DateTime.now}] Dropped lower, assuming proxy reset - continuing"
                        rframes[r] = 0
                        next
                end
                if rframes[r] < dframes
                        puts "[#{DateTime.now}] Delta +#{dframes-rframes[r]}"
                        rframes[r] = dframes
                        next
                end
        end
end

sleep 5

end
