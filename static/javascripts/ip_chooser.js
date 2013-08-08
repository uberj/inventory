function build_select_state(options){
    var pks = [];
    options.each(function(i, option){
        if($(option).val()){
          pks.push(parseInt($(option).val(), 'base-ten'));
        }
    });
    return pks;
}

function chosen_init(target_el_id, find_related_url){
  var config = {
      '.chosen-select'           : {},
      '.chosen-select-deselect'  : {allow_single_deselect:true},
      '.chosen-select-no-single' : {disable_search_threshold:10},
      '.chosen-select-no-results': {no_results_text:'Oops, nothing found!'},
      '.chosen-select-width'     : {width:"95%"}
  };
  for (var selector in config) {
      $(selector).chosen(config[selector]);
  }
  $(".chosen-select").chosen().change(function (el){
      var choice_option = $(el.target);
      var choice_type = $(el.target).data('choice-type');
      var choice_pk = $(el.target).find('option:selected').val();
      var state = {
          choice: [choice_type, choice_pk],
          sites: build_select_state($('#choose-site .choice')),
          networks: build_select_state($('#choose-network .choice')),
          vlans: build_select_state($('#choose-vlan .choice'))
      };
      console.log("state: ");
      console.log(JSON.stringify(state));
      $.ajax({
        url: find_related_url,
        type: "POST",
        data: JSON.stringify(state),
        success: function(result){
          console.log("results: ");
          console.log(result);
          var new_state = $.parseJSON(result);

          function replace_options(select_id, value_and_labels, choice_option){
            var select_el = $(select_id);
            if(select_id == '#' + choice_option.attr('id')){
              $(select_id + " option:not(selected)").remove();
            } else {
              $(select_id + " option:gt(0)").remove();
            }
            $.each(value_and_labels, function(key, o) {
              select_el.append(
                $("<option></option>").attr("value", o.value).attr('class', 'choice').text(o.label)
              );
            });
            $(select_id).trigger("chosen:updated");
          }

          replace_options('#choose-network', new_state.networks, choice_option);
          replace_options('#choose-site', new_state.sites, choice_option);
          replace_options('#choose-vlan', new_state.vlans, choice_option);
        },
        error: function(e){
          var newDoc = document.open("text/html", "replace");
          newDoc.write(e.responseText);
          newDoc.close();
        }
      });
  });
}

