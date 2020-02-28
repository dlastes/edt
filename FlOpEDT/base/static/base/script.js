function fetch_rooms() {

    $.ajax({
        type: "GET",
        dataType: 'json',
        url: data,
        async: true,
        contentType: "text/json",
        success: function(msg, ts, req) {

        types = []

        for(const t in msg.roomtypes){
            types.push(t);
            document.write(t + "\n")


        }
        console.log(types)

        },
        error: function(msg) {
            console.log("error");
        }
    })
}

function