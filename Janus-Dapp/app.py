from flask import Flask, render_template, request,redirect,url_for,session
import json
import contractutils as cu

app = Flask(__name__)
w3 = None
contract = None

def setup():
	global w3, contract
	w3 = cu.get_connection()
	contract = cu.get_contract(w3)
@app.route('/')
def main_page():
	setup()
	return render_template("index.html")
@app.route('/ship')
def ship_page():
	if(contract == None):
		setup()
	address = request.args.get('address')
	if(cu.shipment_exists(contract, address)):
		driver = cu.get_shipment_driver(contract, address)
		status = cu.get_shipment_status(contract, address)
		return render_template("shipview.html", address=address,driver=driver, status=status)
	return render_template("ship.html", address=address)

@app.route('/api/updatestatus', methods=['POST'])
def update_status():
	if(contract == None):
		setup()
	address = request.form.get('address')
	pk = request.form.get('pk')
	status = eval(request.form.get('status'))
	message = ""
	try:
		result = cu.update_driver_status(address, pk, w3, contract, status)
		if(result["status"] == 1):
			message = "successfully updated"
		else:
			message = "unsuccessful"
		return message
	except Exception as E:
		msg = str(E)
		return msg
	
@app.route('/api/claimpackage', methods=['POST'])
def claiming_package():
	if(contract == None):
		setup()
	address = request.form.get('address')
	pk = request.form.get('pk')
	message = ""
	try:
		result = cu.claim_package(address, pk, w3, contract)
		if(result["status"] == 1):
			message = "successfully updated"
		else:
			message = "unsuccessful"
		return message
	except Exception as E:
		msg = str(E)
		return msg
	
@app.route('/api/dropoff', methods=['POST'])
def droppin_pack():
	if(contract == None):
		setup()
	address = request.form.get('address')
	pk = request.form.get('pk')
	message = ""
	try:
		result = cu.dropoff_package(address, pk, w3, contract)
		if(result["status"] == 1):
			message = "successfully updated"
		else:
			message = "unsuccessful"
		return message
	except Exception as E:
		msg = str(E)
		return msg




@app.route('/enter', methods=['POST'])
def enter():
	if(contract == None):
		setup()
	address = request.form.get('address')
	print(address)
	if(not cu.valid_address(address)):
		return render_template("index.html", message="invalid address")
	action = request.form.get('action')
	if(action == "ship"):
		if(cu.shipment_exists(contract, address)):
			driver = cu.get_shipment_driver(contract,address)
			status = cu.get_shipment_status(contract, address)
			if(status == 1):
				driver = cu.get_shipment_driver(contract, address)
				return render_template("shipview.html", address=address,driver=driver, status=status)
			return render_template("shipview.html", address=address,driver=driver, status=status)
		return render_template("ship.html",address=address)
	elif(cu.driver_exists(contract, address)):
		driving = cu.get_driver_status(contract, address) == 1
		status = cu.driver_available(contract, address)
		if(driving):
			package = cu.get_driver_package(contract, address)
			lon = cu.get_driver_goal_long(contract, address)
			lat = cu.get_driver_goal_lat(contract, address)
			goal = "to " + str(lon) + 'longitude and ' + str(lat) + " latitude"
			return render_template("driverhome.html", address=address,driving=driving, status=status, package=package, goal=goal)
		return render_template("driverhome.html", address=address, status=status, driving=driving)
	return render_template("driversignup.html", address=address)

@app.route('/api/ship', methods=['POST'])
def ship_form():
	if(contract == None):
		setup()
	address = request.form.get('address')
	pk = request.form.get('pk')
	pickup = request.form.get('pickup').split(",")
	dropoff = request.form.get('dropoff').split(",")
	length = request.form.get('length')
	width = request.form.get('width')
	height = request.form.get('height')
	weight = request.form.get('weight')
	print(address, pk, pickup, dropoff, length, width, height, weight)
	try:
		long_p,lat_p = int(pickup[0]), int(pickup[1])
		long_ar, lat_a = int(dropoff[0]),int(dropoff[1])
		width = int(width)
		height = int(height)
		length = int(length)
		weight = int(weight)
	except Exception as e:
		print("invalid")
		print(e)
		message="invalid long/lat coordinates.  ints > 0 only"
		return message
	print(address,pk,w3,contract,pickup,dropoff,address,width,height,weight)
	print(address)
	try:
		result = cu.ship_package(address,pk,w3,contract,long_p,lat_p,long_ar,lat_a,weight,height,width, length)
		if(result["status"] == 1):
			return "You have successfully signed up! " + "<a href='./ship?address="+address+"'>Home</a>"
		else:
			return "unable to process your request"
	except Exception as e:
		msg = str(e)
		return msg

@app.route('/api/estimatecost', methods=['POST'])
def estimate_cost():
	if(contract == None):
		setup()
	pickup = request.form.get('pickup').split(",")
	dropoff = request.form.get('dropoff').split(",")
	try:
		long_p,lat_p = int(pickup[0]), int(pickup[1])
		long_ar, lat_a = int(dropoff[0]),int(dropoff[1])
		return str(cu.estimate_shipping(contract, long_p,lat_p,long_ar, lat_a)) + " wei"
	except Exception as e:
		print(e)
		return 'invalid long/lat coordinates'
@app.route('/signup', methods=['GET'])
def driver_signup():
	if(contract == None):
		setup()
	address = request.args.get('address')
	if(cu.driver_exists(contract, address)):
		driving = cu.get_driver_status(contract, address) == 1
		status = cu.driver_available(contract, address)
		if(driving):
			package = cu.get_driver_package(contract, address)
			lon = cu.get_driver_goal_long(contract, address)
			lat = cu.get_driver_goal_lat(contract, address)
			goal = "to " + str(lon) + 'longitude and ' + str(lat) + " latitude"
			return render_template("driverhome.html", address=address,driving=driving, status=status, package=package, goal=goal)
		return render_template("driverhome.html", address=address, status=status, driving=driving)
	return render_template("driversignup.html", address=address)
@app.route('/api/signup', methods=['POST'])
def driver_signup_api():
	if(contract == None):
		setup()
	address = request.form.get('address')
	print("address", address)
	if(cu.driver_exists(contract, address)):
		return "Driver already exists"
	pk = request.form.get('pk')
	location = request.form.get('location')
	length = request.form.get('length')
	width = request.form.get('width')
	height = request.form.get('height')
	capacity = request.form.get('weight')
	valid_dimensions = True
	dims = [length, width, height, capacity]
	dims.extend(location.split(","))
	print(dims)
	for i in dims:
		try:
			if(int(i) <= 0):
				valid_dimensions = False
		except:
			valid_dimensions = False
	if(len(location.split(",")) != 2):
		valid_dimensions = False
	if(not valid_dimensions):
		return "Invalid signup paramaters"
	try:
		l = location.split(",")
		lat = int(l[0])
		lon = int(l[1])
		width = int(width)
		height = int(height)
		capacity = int(capacity)
		length = int(length)
		result = cu.signup_driver(address,pk,w3,contract,lat,lon,length,width,height,capacity)
		if(result["status"] == 1):
			return "You have successfully signed up! " + "<a href='./signup?address="+address+"'>Home</a>"
		return "Sorry.  We're unable to process your request"
	except ValueError:
		return "invalid private key or insufficient funds"
if __name__=="__main__":
    app.run("localhost", 8080, debug = True)