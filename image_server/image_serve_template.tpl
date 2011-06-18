<!-- images, prev_page_num, next_page_num, move_dir, -->
  <html>
  <head>
    <link rel="stylesheet" type="text/css" href="http://craigsworks.com/projects/qtip2/packages/latest/jquery.qtip.css" /> 
    <script type="text/javascript" src="http://gettopup.com/releases/latest/top_up-min.js"></script>
    <script type="text/javascript" src="http://craigsworks.com/projects/qtip2/packages/latest/jquery.qtip.js"></script> 
  </head>
  <body>
  <a href="/p/{{prev_page_num}}">Prev</a><br>
  <a href="/p/{{next_page_num}}">Next</a><br>
  <table>
    %for x in images:
        <div style="float:left;width:100px;">
	    <a href="/image/i/{{x}}" title="{{x}}" class="top_up" target="_blank"><img src="/image/t/{{x}}" style="height:50;max-width:100"/></a>
            <br>
	    %if movedir is not None:
	        <input IMG="{{x}}" 
		       class="move_button" style="height:30" type="submit" 
		       value="Move">
            %end
         </div>
    %end
  
  <script type="text/javascript">
$(document).ready(function()
{
// Match all <A/> links with a title tag and use it as the content (default).
$('a[title]').qtip();
});
    // Use jQuery to handle moving images
    $("input.move_button").click(function () {
	var td = this
	var url = '/move/' + $(this).attr('IMG');
	$.ajax({
	    url: url,
	    type: "POST",
	    success: function(data) { 
		$(td).closest('div').hide()
	    },
	    error: function (data) {
		console.error(data.responseText);
	    }
	})
    })
  </script>

  </body>
  </html>
