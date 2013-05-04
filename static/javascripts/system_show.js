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

    $('#id_show_all_ranges').click(function(){
        if($(this).attr("checked")){
            $("#id_sreg_range option").each(function(){
                $(this).css("display","");
            });
        } else {
            $("#id_sreg_range option").each(function(){
                if ($(this).attr('relevant') === 'false'){
                    $(this).css("display","none");
                }
            });
        }
    });
    $('#id_show_all_ranges').attr("checked", ""); // Default

    $(".add_new_sreg").click(function(){
        make_smart_name_get_domains($("#id_sreg_fqdn"), true);
        $.ajax({
                type: "GET",
                url: "/core/range/get_all_ranges_ajax/",
                data: {'system_pk': system_id},
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                beforeSend: function(){
                        $("#id_sreg_range").get(0).options[0] = new Option("Loading...", "");
                },
                success: function(msg) {
                        $("#id_sreg_range").get(0).options.length = 0;
                        $("#id_sreg_range").get(0).options[0] = new Option("Select Range", "");
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
                            $("#id_sreg_range").get(0).options[$("#id_sreg_range").get(0).options.length] = option
                        });
                        if($('#id_show_all_ranges').attr("checked")){
                            $("#id_sreg_range option").each(function(){
                                $(this).css("display","");
                            });
                        } else {
                            $("#id_sreg_range option").each(function(){
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
                title: 'Create new registration',
                autoShow: true,
                width: 700,
                buttons: {
                    "Save": function() {
                        if(!$("#id_sreg_ip_address").val() && !$("#id_sreg_range").val() && $('#id_auto_assign_ip').is(':checked')){
                            alert("Select a range");
                            return;
                        }
                        if(!$("#id_sreg_ip_address").val()){
                            alert("IP Address Required");
                            return;
                        }
                        $.post('/en-US/systems/create_static_registration/' + system_id + '/',
                            {
                                'sreg_form': $('#sreg-form').serialize(),
                                'hw_adapter_forms': $('#hw-adapter-form').serialize()
                            },
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
                            $("#id_sreg_range").get(0).options.length = 0;
                            $( this ).dialog( "close" );
                        }
                },
                close: function(event, ui){
                    $("#id_sreg_range").get(0).options.length = 0;
                }

        }); // End dialog
        d.show();
        return false;
    // end of .system_quick_sreg.click()
    });

    // Use fqdn or auto creation options.
    $("#id_override_fqdn").click(function(){
        if($(this).attr("checked")){
            $("#id_sreg_fqdn").attr("readonly", "");
        } else {
            $("#id_sreg_fqdn").attr("readonly", "readonly");
        }

    });
    // Defaults
    $("#id_sreg_fqdn").attr("readonly", "readonly");
    $("#id_override_fqdn").attr("checked", "");

    function auto_assign_ip(the_range){
        if (the_range){
            $.get('/core/range/get_next_available_ip_by_range/' + the_range + '/',
                function(data){
                    var obj = jQuery.parseJSON(data);
                    if(obj.success == true){
                        //$("#id_sreg_ip_address").attr("disabled", "disabled");
                        $("#id_sreg_ip_address").val(obj.ip_address);
                        $('#id_sreg_ip_address').keyup();  // Set the views!
                    } else {
                        alert(obj.error);
                    }
            });
        } else {
            alert("Please select a range.");
            $("#id_sreg_ip_address").val('Auto Assign');
        }
    }

    $("#id_auto_assign_ip").click(function(){
            if($(this).attr("checked")){
                var the_range = $("#id_sreg_range").val();
                auto_assign_ip(the_range);
                $("#id_sreg_ip_address").attr("readonly", "readonly");
            } else {
                $("#id_sreg_ip_address").attr("readonly", "");
                if ($("#id_sreg_ip_address").val() === 'Auto Assign'){
                    $("#id_sreg_ip_address").val('');
                }
                // Reset the range select but don't clear the IP
                $("#id_sreg_range").attr('selectedIndex',0);
            }

    });

    $("#id_sreg_range").change(function(){
        if ($("#id_auto_assign_ip").attr("checked")){
            auto_assign_ip($(this).val());
        }
        if ($('#id_override_fqdn').attr('checked') === false) {
            var suggested_fqdn = $("#id_sreg_range option:selected").attr('suggested_fqdn');
            console.log("Suggesting: "+ suggested_fqdn);
            $('#id_sreg_fqdn').val(suggested_fqdn);
            $('.hw_option_hostname').val(suggested_fqdn);
        }
    });
    // Default IP
    $("#id_auto_assign_ip").attr("checked", "checked"); // Set it to auto assign
    $("#id_sreg_ip_address").val('Auto Assign');
    $("#id_sreg_ip_address").attr('readonly', 'readonly');
    bind_view_ip_type_detection();

    /*
     * Dynamically adding Hardware Adapters
     */

    $("#hwadapter-tables").data('adapterCounter', 0);
    $('#hwadapter-tables').find('.remove-hwadapter').css('visibility', 'hidden');

    $('#btnMore').click(function() {
        var hwtable, blocks, newBlock, newEntry, nextFree;
        var removeButton, newTTL;

        hwtable = $('#hwadapter-tables');
        adapterCounter = hwtable.data('adapterCounter');
        nextFree = adapterCounter + 1;
        hwtable.data('adapterCounter', nextFree);
        blocks = hwtable.find('.hwadapter-table');
        newBlock = $(blocks.last()).clone();
        $(newBlock).find('input').each(function (i, el) {
            $(el).attr('name', $(el).attr('name').replace(nextFree - 1, nextFree));
            $(el).attr('id', $(el).attr('id').replace(nextFree - 1, nextFree));
        });

        // Bind remove handler
        removeButton = newBlock.find('.remove-hwadapter');
        $(removeButton).css('visibility', 'visible');
        removeButton.click(function(){
            $(this).closest('table').remove();
        });
        newBlock.insertAfter(blocks.last());
    });

    // gdmit this code is duplicate code!  static/javascripts/dns_form_utils.js

    function bind_view_ip_type_detection() {
        // If an ip starts with '10' automatically set the private view
        // If an ip starts with '63.245' automatically set the public view
        var public_prefixs = ['63.245', '2620:0101', '2620:101'];
        var private_prefixs = ['10'].concat(public_prefixs);
        var found = false; // Help us only do view detect once

        var i; // loop var

        $('#id_sreg_ip_address').keyup(function(){
            set_ip_type($('#id_sreg_ip_address').val());
            function do_detect(prefixs, view_el){
                var ip_str = $('#id_sreg_ip_address').val();
                for(i = 0; i < prefixs.length; i++) {
                    if (ip_str.substring(0, prefixs[i].length) === prefixs[i]) {
                        $(view_el).attr('checked', 'checked');
                        found = true;
                        console.log("ckecked");
                        break;
                    }
                }
            }
            if (!found) {  // Only do view detect if we havne't done it before
                do_detect(private_prefixs, '#id_sreg_views_0');
                do_detect(public_prefixs, '#id_sreg_views_1');
            }
        });

        function set_ip_type(ip){
            if(ip.indexOf('.') > 0) {
                $("#id_ip_type option[value='4']").attr("selected", "selected");
                $("#id_ip_type option[value='6']").removeAttr("selected");
            } else if(ip.indexOf(':') > 0) {
                $("#id_ip_type option[value='4']").removeAttr("selected");
                $("#id_ip_type option[value='6']").attr("selected", "selected");
            }
        }
    }

});
