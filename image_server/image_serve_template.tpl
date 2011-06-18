<!-- images, prev_page_num, next_page_num, move_dir, -->
  <html>
  <head>
    <link rel="stylesheet" type="text/css" href="http://craigsworks.com/projects/qtip2/packages/latest/jquery.qtip.css" /> 
    <script type="text/javascript" src="http://gettopup.com/releases/latest/top_up-min.js"></script>
    <script type="text/javascript" src="http://craigsworks.com/projects/qtip2/packages/latest/jquery.qtip.js"></script> 
  </head>
  <body>
  <span style="margin:10px;font-size:150%"><a href="/p/{{prev_page_num}}">Prev</a></span>
  <span style="margin:10px;font-size:150%"><a href="/p/{{next_page_num}}">Next</a></span>
  <div>
    %for x in images:
        <div style="float:left;max-width:100px;text-align:center;margin:15px 2px">
          <div>
            <a title="{{x}}">info1</a>
          </div>
	  <div>
	    <a href="/image/i/{{x}}" class="top_up" toptions="effect=hide,overlayClose=0" target="_blank"><img src="/image/t/{{x}}" style="height:50;max-width:100"/></a>
	  </div>
	  <div>
	    %if movedir is not None:
	        <input img="{{x}}" 
		       class="move_button" style="height:30;" type="submit" 
		       value="Move">
            %end
	  </div>
         </div>
    %end
  </div>
  <script type="text/javascript">
TopUp.addPresets({
   '.top_up a': {
       effect:'hide'
   }
})
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
                var outer = $(td).closest('div').parent()
                var width = outer.width()
                outer.empty()
                outer.width(width)
	    },
	    error: function (data) {
		console.error(data.responseText);
	    }
	})
    })
  </script>

  </body>
  </html>
