  <html>
  <head>
    <script type="text/javascript" src="http://code.jquery.com/jquery-latest.min.js"></script>
    <link rel="stylesheet" type="text/css" href="http://craigsworks.com/projects/qtip2/packages/latest/jquery.qtip.css" /> 
    <script type="text/javascript" src="http://gettopup.com/releases/latest/top_up-min.js"></script>
    <script type="text/javascript" src="http://craigsworks.com/projects/qtip2/packages/latest/jquery.qtip.js"></script> 
  </head>
  <body>
  %if prev_page_num is not None:
      <span style="margin:10px;font-size:150%"><a href="/{{auth_key}}/p/{{prev_page_num}}">Prev</a></span>
  %end
  %if next_page_num is not None:
      <span style="margin:10px;font-size:150%"><a href="/{{auth_key}}/p/{{next_page_num}}">Next</a></span>
  %end
  <span style="margin:10px;font-size:150%"><a href="/{{auth_key}}/refresh/">Update</a></span>
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
    %for group_name, images in group_images:
    <div style="float:left;clear:left;"><h2>{{group_name}}</h2></div><div style="clear:left;float:left"></div>
    %for x in images:
        <div style="float:left;max-width:{{thumbsize}}px;text-align:center;margin:15px 1px">
          <div>
            <a title="{{x}}">info</a>
          </div>
	  <div>
	    <a href="/{{auth_key}}/image/i/{{x}}" class="top_up" toptions="effect=hide, modal=1, type=image" target="_blank"><img src="/{{auth_key}}/image/t/{{x}}" style="height:{{thumbsize}}px;max-width:{{thumbsize}}px"/></a>
	  </div>
	  %for i, movedir in zip(range(len(movedirs)), movedirs):
	  <div>
	        <input img="{{x}}" 
		       class="move_button" style="width:{{thumbsize}};height:25;" type="submit"
		       index="{{i}}" value="{{i}}">
	  </div>
          %end
         </div>
    %end
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
	var url = '/{{auth_key}}/move/' + $(this).attr('IMG');
	$.ajax({
	    url: url,
	    type: "POST",
            data: {"index": $(td).attr('index')},
	    success: function(data) { 
            $(td).closest('div').parent().css("visibility", "hidden");
	    },
	    error: function (data) {
		console.error(data.responseText);
	    }
	})
    })
  </script>

  </body>
  </html>
