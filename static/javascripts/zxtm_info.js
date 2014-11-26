/*
 * These functions help pull in data from the zxtm slurp data source and put them into the UI for people to see.
 */

function showZXTMInfo(root) {
  root.find('.possible-zxtm-info').each(function (i, needs_info_el) {
      $.get('/en-US/slurpee/zxtm/zxtm_info/', {'ident': $(needs_info_el).html()},
        function(data) {
          if (!data) {
            console.log('no data for: ');
            console.log(needs_info_el);
          } else {
            console.log('found data for: ');
            $(needs_info_el).css('color', 'blue');
            console.log(needs_info_el);
            $(needs_info_el).append(data);
            $(needs_info_el).myTooltip();
          }
        }
      );
  });
}

$(document).ready(function (){
  showZXTMInfo($(document));
});
