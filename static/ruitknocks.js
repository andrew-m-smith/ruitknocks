var carriers = [];
var current = []

$(document).ready(function(){
	$.post("../start", function(data){
		parseResponse(data);
	});

	function parseResponse(response){
		var knocks = response.knocks;
		current = response.currentGame;
		carriers = response.carriers;
		$("#knockListContainer ul").html("")
		$.each(knocks, function(i, knock){
			$("#knockListContainer ul").append("<li>"+knock+"</li>");
		});
		if(current[0] != null && current[1] != null){
			$("#currentGameContainer").html("<h2>NOW PLAYING</h2>" + current[0] + " Versus " + current[1]);
		}
		$("#formContainer").html(response.response);
	}

	$(".knockArea").on("click", function(){
		var form = "";
		form += '<form id="knock">';
		form += '<h2>KNOCK</h2>';
		form += 'Player 1 Swipe<br><input type="text" name="playerOne" maxlength="9"><br>';
		form += 'Player 2 Swipe<br><input type="text" name="playerTwo" maxlength="9"><br>';
		$("#formContainer").html(form);
		$("[name='playerOne']").focus();
	});

	$(".cancelArea").on("click", function(){
		var form = "";
		form += '<form id="cancelKnock">';
		form += '<h2>CANCEL KNOCK</h2>';
		form += 'Player 1 Swipe<br><input type="text" name="playerOne" maxlength="9"><br>';
		form += 'Player 2 Swipe<br><input type="text" name="playerTwo" maxlength="9"><br>';
		$("#formContainer").html(form);
		$("[name='playerOne']").focus();
	});

	$(".checkArea").on("click", function(){
		var form = "";
		form += '<form id="checkKnock">';
		form += '<h2>CHECK KNOCK</h2>';
		form += 'Player 1 Swipe<br><input type="text" name="playerOne" maxlength="9"><br>';
		form += 'Player 2 Swipe<br><input type="text" name="playerTwo" maxlength="9"><br>';
		$("#formContainer").html(form);
		$("[name='playerOne']").focus();
	});

	$(".newArea").on("click", function(){
		var form = "";
		form += '<form id="newPlayer">';
		form += '<h2>NEW PLAYER</h2>'
		form += 'First Name<br><input type="text" name="firstName"><br>';
		form += 'Last Name<br><input type="text" name="lastName"><br>';
		form += 'Phone Number<br><input type="text" name="phoneNumber" maxlength="10"><br>';
		form += 'Carrier<br><select name="carrier">';
		form += '<option></option>'
		$.each(carriers, function(i, carrier){
			form += '<option>' + carrier + '</option>'
		});
		form += '</select><br>'
		form += 'Swipe Card<br><input type="text" name="playerID" maxlength="9"><br>';
		$("#formContainer").html(form);
		$("[name='firstName']").focus();
	});

	$(".endArea").on("click", function(){
		var form = "";
		if(current[0] !== null && current[1] !== null){
			form += '<form id="endGame">';
			form += '<h2>How many cups did you get?</h2>'
			form += current[0]
			form += '<br><input type="text" name="cupsOne" maxlength="2"><br>';
			form += current[1]
			form += '<br><input type="text" name="cupsTwo" maxlength="2"><br>';
		}else{
			form += '<h2>NO GAMES IN PROGRESS</h2>'
		}
		$("#formContainer").html(form);
		$("[name='cupsOne']").focus();
	});

	$(document).on("keypress", "[name='cupsOne']", function(e){
		code = e.which;
		if(code == 13){
			if( $("[name='cupsOne']").val().length < 1){
				$("[name='cupsOne']").val("");
			}else{
				$("[name='cupsTwo']").focus();
			}
		}else if(code < 48 || code > 57) return false;
	});

	$(document).on("keypress", "[name='cupsTwo']", function(e){
		code = e.which;
		if(code == 13){
			if( $("[name='cupsTwo']").val().length < 1){
				$("[name='cupsTwo']").val("");
			}else{
				$("form").submit();
			}
		}else if(code < 48 || code > 57) return false;
	});

	$(document).on("keypress", "[name='playerOne']", function(e){
		code = e.which;
		if(code == 13){
			if( $("[name='playerOne']").val().length < 9){
				$("[name='playerOne']").val("");
			}else{
				$("[name='playerTwo']").focus();
			}
		}else if(code < 48 || code > 57) return false;
	});

	$(document).on("keypress", "[name='playerTwo']", function(e){
		code = e.which;
		if(code == 13){
			if( $("[name='playerTwo']").val().length < 9){
				$("[name='playerTwo']").val("");
			}else{
				$("form").submit();
			}
		}else if(code < 48 || code > 57) return false;
	});

	$(document).on("keypress", "[name='playerID']", function(e){
		code = e.which;
		if(code == 13){
			if( $(this).val().length < 9){
				$(this).val("");
			}else{
				$("form").submit();
			}
		}else if(code < 48 || code > 57) return false;
	});

	$(document).on("keypress", "[name='phoneNumber']", function(e){
		code = e.which;
		if(code == 13){
			if( $(this).val().length < 10){
				$(this).val("");
			}else{
				$("[name='carrier']").focus();
			}
		}else if(code < 48 || code > 57) return false;
	});

	$(document).on("keypress", "[name='firstName']", function(e){
		code = e.which;
		if(code == 13){
			if( $(this).val() !== ""){
				$("[name='lastName']").focus();
			}
		}else if((code < 65 || code > 90) && (code < 97 || code > 122)) return false;
	});

	$(document).on("keypress", "[name='lastName']", function(e){
		code = e.which;
		if(code == 13){
			if( $(this).val() !== ""){
				$("[name='phoneNumber']").focus();
			}
		}else if((code < 65 || code > 90) && (code < 97 || code > 122)) return false;
	});

	$(document).on("change", "[name='carrier']", function(){
		if( $(this).val() !== ""){
			$("[name='playerID']").focus();
		}
	});

	$(document).on("submit", "#knock", function(){
		var err = "";
		var form = $(this).serializeArray();
		var re = /[\d]{9}/;
		$.each(form, function(i, field){
			if(field.name === "playerOne"){
				if(!(re.test(field.value))){
					err += "Player One ID is invalid.\n";
				}
			}else if (field.name === "playerTwo"){
				if(!(re.test(field.value))){
					err += "Player Two ID is invalid.\n";
				}
			}
		});
		if(err){
			alert(err);
		}else{
			$("#formContainer").html("Please wait...")
			$.post("../knock", form, function(data){
				parseResponse(data);
			});
		}
		return false;
	});


	$(document).on("submit", "#cancelKnock", function(){
		var err = "";
		var form = $(this).serializeArray();
		var re = /[\d]{9}/;
		$.each(form, function(i, field){
			if(field.name === "playerOne"){
				if(!(re.test(field.value))){
					err += "Player One ID is invalid.\n";
				}
			}else if (field.name === "playerTwo"){
				if(!(re.test(field.value))){
					err += "Player Two ID is invalid.\n";
				}
			}
		});
		if(err){
			alert(err);
		}else{
			$("#formContainer").html("Please wait...")
			$.post("../cancel", form, function(data){
				parseResponse(data);
			});
		}
		return false;
	});


	$(document).on("submit", "#checkKnock", function(){
		var err = "";
		var form = $(this).serializeArray();
		var re = /[\d]{9}/;
		$.each(form, function(i, field){
			if(field.name === "playerOne"){
				if(!(re.test(field.value))){
					err += "Player One ID is invalid.\n";
				}
			}else if (field.name === "playerTwo"){
				if(!(re.test(field.value))){
					err += "Player Two ID is invalid.\n";
				}
			}
		});
		if(err){
			alert(err);
		}else{
			$("#formContainer").html("Please wait...")
			$.post("../check", form, function(data){
				parseResponse(data);
			});
		}
		return false;
	});


	$(document).on("submit", "#newPlayer", function(){
		var err = "";
		var form = $(this).serializeArray();
		var re;
		$.each(form, function(i, field){
			if(field.name === "playerID"){
				re = /[\d]{9}/;
				if(!(re.test(field.value))){
					err += "Player One ID is invalid.\n";
				}
			}else if (field.name === "firstName"){
				re = /^[A-Za-z]+$/;
				if(!(re.test(field.value))){
					err += "Player first name is invalid.\n";
				}
			}else if (field.name === "lastName"){
				re = /^[A-Za-z]+$/;
				if(!(re.test(field.value))){
					err += "Player last name is invalid.\n";
				}
			}else if (field.name === "phoneNumber"){
				re = /[\d]{10}/;
				if(!(re.test(field.value))){
					err += "Phone Number is invalid.\n";
				}
			}
		});
		if(err){
			alert(err);
		}else{
			$("#formContainer").html("Please wait...")
			$.post("../new", form, function(data){
				parseResponse(data);
			});
		}
		return false;
	});

		$(document).on("submit", "#endGame", function(){
		var err = "";
		var form = $(this).serializeArray();
		var re = /^\d+$/;
		$.each(form, function(i, field){
			if(field.name === "cupsOne"){
				if(!(re.test(field.value))){
					err += "Cups One is invalid.\n";
				}
			}else if (field.name === "cupsTwo"){
				if(!(re.test(field.value))){
					err += "Cups Two is invalid.\n";
				}
			}
		});
		if(err){
			alert(err);
		}else{
			$("#formContainer").html("Please wait...")
			$.post("../end", form, function(data){
				parseResponse(data);
			});
		}
		return false;
	});

});