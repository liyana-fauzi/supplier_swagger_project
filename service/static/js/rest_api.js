$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#supplier_id").val(res._id);
        $("#name").val(res.name);
        $("#category").val(res.category);
        if (res.preferred == true) {
            $("#preferred").val("true");
        } else {
            $("#preferred").val("false");
        }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#name").val("");
        $("#category").val("");
        $("#preferred").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Supplier
    // ****************************************

    $("#create-btn").click(function () {

        var name = $("#name").val();
        var category = $("#category").val();
        var preferred = $("#preferred").val() == "true";

        var data = {
            "name": name,
            "category": category,
            "preferred": preferred
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/suppliers",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Supplier
    // ****************************************

    $("#update-btn").click(function () {

        var supplier_id = $("#supplier_id").val();
        var name = $("#name").val();
        var category = $("#category").val();
        var preferred = $("#preferred").val() == "true";

        var data = {
            "name": name,
            "category": category,
            "preferred": preferred
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/suppliers/" + supplier_id,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Supplier
    // ****************************************

    $("#retrieve-btn").click(function () {

        var supplier_id = $("#supplier_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/suppliers/" + supplier_id,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Supplier
    // ****************************************

    $("#delete-btn").click(function () {

        var supplier_id = $("#supplier_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/suppliers/" + supplier_id,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Supplier has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#supplier_id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for a Supplier
    // ****************************************

    $("#search-btn").click(function () {

        var name = $("#name").val();
        var category = $("#category").val();
        var preferred = $("#preferred").val() == "true";

        var queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (category) {
            if (queryString.length > 0) {
                queryString += '&category=' + category
            } else {
                queryString += 'category=' + category
            }
        }
        if (preferred) {
            if (queryString.length > 0) {
                queryString += '&preferred=' + preferred
            } else {
                queryString += 'preferred=' + preferred
            }
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/suppliers?" + queryString,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:10%">ID</th>'
            header += '<th style="width:40%">Name</th>'
            header += '<th style="width:40%">Category</th>'
            header += '<th style="width:10%">Available</th></tr>'
            $("#search_results").append(header);
            var firstSupplier = "";
            for(var i = 0; i < res.length; i++) {
                var Supplier = res[i];
                var row = "<tr><td>"+Supplier._id+"</td><td>"+Supplier.name+"</td><td>"+Supplier.category+"</td><td>"+Supplier.preferred+"</td></tr>";
                $("#search_results").append(row);
                if (i == 0) {
                    firstSupplier = Supplier;
                }
            }

            $("#search_results").append('</table>');

            // copy the first result to the form
            if (firstSupplier != "") {
                update_form_data(firstSupplier)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
