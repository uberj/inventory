function display_inpage_search_results(query, results_selector, callback) {
    $.get('/en-US/core/search/search_ajax/',
        {
          'format': 'table',
          'search': query + ' AND !(type=:SYSTEM OR type=:SREG)',
        },
        function(data) {
            if (!data) {
              console.log('no dns data');
            } else {
                $(results_selector).empty();
                $(results_selector).append(data);
            }
            callback();
        });
}


function goto_range(ip_str, ip_type){
    $.get('/core/range/find_range/?ip_str='+ip_str+'&ip_type=' + ip_type, do_redirect);
}

function do_redirect(e) {
    var obj = jQuery.parseJSON(e);
    if (obj.success){
        window.open(obj.redirect_url);
    } else {
        alert(obj.message);
    }
}

$(document).ready(function() {
    var system_id = $('#meta-data').attr('data-system-id');

    $("a.goto_range").click(function (){
        var args = $(this).attr("rel").split('|');
        var ip_str = args[0];
        var ip_type = args[1];
        $.get('/core/range/find_range/?ip_str='+ip_str+'&ip_type=' + ip_type, do_redirect);
    });

    $('#show_all_ranges').click(function(){
        if($(this).attr("checked")){
            $("#sreg_range option").each(function(){
                $(this).css("display","");
            });
        } else {
            $("#sreg_range option").each(function(){
                if ($(this).attr('relevant') === 'false'){
                    $(this).css("display","none");
                }
            });
        }
    });
    $('#show_all_ranges').attr("checked", ""); // Default

    $(".add_new_sreg").click(function(){
        make_smart_name_get_domains($("#sreg_fqdn"), true);
        $.ajax({
                type: "GET",
                url: "/core/range/get_all_ranges_ajax/",
                data: {'system_pk': system_id},
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                beforeSend: function(){
                        $("#sreg_range").get(0).options[0] = new Option("Loading...", "");
                },
                success: function(msg) {
                        $("#sreg_range").get(0).options.length = 0;
                        $("#sreg_range").get(0).options[0] = new Option("Select Range", "");
                        $.each(msg, function(index, item) {
                            var tld = $("#hostname_dd").html().split('.').pop();
                            // Build a suggested FQDN and store it on the range option
                            if (tld === 'com' || tld === 'net' || tld === 'org'){
                                suggested_fqdn = "mozilla." + tld;
                            } else {
                                suggested_fqdn = "mozilla.com";
                            }
                            if (item.site !== ''){
                                suggested_fqdn = item.site + '.' + suggested_fqdn;
                            }
                            if (item.vlan !== ''){
                                suggested_fqdn = item.vlan + '.' + suggested_fqdn;
                            }
                            suggested_fqdn = $("#hostname_dd").html().split('.')[0] + '.' + suggested_fqdn
                            var option = new Option(item.display, item.id);
                            $(option).attr('suggested_fqdn', suggested_fqdn);
                            $(option).attr('relevant', item.relevant);
                            if (!item.relevant) {
                                $(option).css("display", "none");
                            }
                            $("#sreg_range").get(0).options[$("#sreg_range").get(0).options.length] = option
                        });
                        if($('#show_all_ranges').attr("checked")){
                            $("#sreg_range option").each(function(){
                                $(this).css("display","");
                            });
                        } else {
                            $("#sreg_range option").each(function(){
                                if ($(this).attr('relevant') === 'false'){
                                    $(this).css("display","none");
                                }
                            });
                        }
                },
                error: function() {
                    alert("Failed to load Ranges");
                }
            }); // End Ajax
        var d = $( "#add-sreg-dialog" ).dialog({
                title: 'Add sreg to System',
                autoShow: true,
                width: 700,
                buttons: {
                    "Save": function() {
                        if(!$("#sreg_range").val() && $('#auto_assign_ip').is(':checked')){
                            alert("Range Required");
                            return;
                        }
                        if(!$("#sreg_ip_address").val()){
                            alert("IP Address Required");
                            return;
                        }
                        $.post('/en-US/systems/create_interface/' + system_id + '/',
                            $('#si-sreg-form').serialize(),
                            function(data){
                                var obj = jQuery.parseJSON(data);
                                if(obj.success == true){
                                    self.location.reload();
                                } else {

                                    alert(obj.error_message);

                                }
                            }).error(function (e) {
                                var newDoc = document.open("text/html", "replace");
                                newDoc.write(e.responseText);
                                newDoc.close();
                                $('#form-message').html("<p>Error</p>");
                            });
                        },
                        Cancel: function() {
                            $("#sreg_range").get(0).options.length = 0;
                            $( this ).dialog( "close" );
                        }
                },
                close: function(event, ui){
                    $("#sreg_range").get(0).options.length = 0;
                }

        }); // End dialog
        d.show();
        return false;
    // end of .system_quick_sreg.click()
    });

    // Use fqdn or auto creation options.
    $("#override_fqdn").click(function(){
        if($(this).attr("checked")){
            $("#sreg_fqdn").attr("readonly", "");
        } else {
            $("#sreg_fqdn").attr("readonly", "readonly");
        }

    });
    // Defaults
    $("#sreg_fqdn").attr("readonly", "readonly");
    $("#override_fqdn").attr("checked", "");

    function auto_assign_ip(the_range){
        if (the_range){
            $.get('/core/range/get_next_available_ip_by_range/' + the_range + '/',
                function(data){
                    var obj = jQuery.parseJSON(data);
                    if(obj.success == true){
                        //$("#sreg_ip_address").attr("disabled", "disabled");
                        $("#sreg_ip_address").val(obj.ip_address);
                    } else {

                        alert(obj.error);

                    }
            });
        } else {
            alert("Please select a range.");
            $("#sreg_ip_address").val('Auto Assign');
        }
    }

    $("#auto_assign_ip").click(function(){
            if($(this).attr("checked")){
                var the_range = $("#sreg_range").val();
                auto_assign_ip(the_range);
                $("#sreg_ip_address").attr("readonly", "readonly");
            } else {
                $("#sreg_ip_address").attr("readonly", "");
                if ($("#sreg_ip_address").val() === 'Auto Assign'){
                    $("#sreg_ip_address").val('');
                }
                // Reset the range select but don't clear the IP
                $("#sreg_range").attr('selectedIndex',0);
            }

    });

    $("#sreg_range").change(function(){
        if ($("#auto_assign_ip").attr("checked")){
            auto_assign_ip($(this).val());
        }
        if ($('#override_fqdn').attr('checked') === false) {
            var suggested_fqdn = $("#sreg_range option:selected").attr('suggested_fqdn');
            console.log("Suggesting: "+ suggested_fqdn);
            $('#sreg_fqdn').val(suggested_fqdn);
        }
    });
    // Default IP
    $("#auto_assign_ip").attr("checked", "checked"); // Set it to auto assign
    $("#sreg_ip_address").val('Auto Assign');
    $("#sreg_ip_address").attr('readonly', 'readonly');
});
