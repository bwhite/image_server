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
  <!-- legend for movedir -->
  %if movedirs:
  <div>
    Legend:
    %for i, movedir in zip(range(len(movedirs)), movedirs):
    <span style="margin:5px;font-size:110%">[{{i}}]: {{movedir}}</span>
    %end
  </div>
  %end
  <div>
    %for x in images:
        <div style="float:left;max-width:{{thumbsize}}px;text-align:center;margin:15px 1px">
          <div>
            <a title="{{x}}">info</a>
          </div>
	  <div>
	    <a href="/image/i/{{x}}" class="top_up" toptions="effect=hide" target="_blank"><img src="/image/t/{{x}}" style="height:{{thumbsize}}px;max-width:{{thumbsize}}px"/></a>
	  </div>
	  %for i, movedir in zip(range(len(movedirs)), movedirs):
	  <div>
	        <input img="{{x}}" 
		       class="move_button" style="width:{{thumbsize}};height:25;" type="submit"
		       value="{{i}}">
	  </div>
          %end
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
