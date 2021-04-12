pragma solidity >=0.6.6;
pragma experimental ABIEncoderV2;

//import "github.com/provable-things/ethereum-api/provableAPI_0.4.25.sol";

/** 
 * @title Ballot
 * @dev Implements voting process along with vote delegation
 */
contract Shipping {
    
   
    struct Location {
        int lat;
        int long;
    }
    
    struct Shipment {
        uint8 width;
        uint8 height;
        uint8 length;
        uint8 weight;
        
        uint8 id;
        
        Location origin;
        Location destination;
        
        address addr;
        address nextShipment;
        address driver;
        
        uint8 status;
        
        uint payment;
    }
    
    struct Driver {
        uint8 weight_capacity;
        
        bool available;
        
        uint8 width; 
        uint8 height;
        uint8 length;
        
        Location loc;
        
        uint8 status;
        address package;
        
        uint8 id;
    }
    
    struct Route {
        Driver driver;
        Shipment package;
        Location pickup;
        Location end;
    }

    bytes32 private ipfs_hash;
    
    mapping(address => Driver) drivers;
    mapping(address => Shipment) shipments;
    mapping(bytes32 => Route) routes;
    
    address queue;

    
    event Dropoff(bytes32 indexed route);
    event Pickup(bytes32 indexed route);
    event DriverRequest(address indexed driver);
    event DriverSignup(address indexed driver);
    event DriverCancel(address indexed driver);
    event RouteRequest(bytes32 indexed route);
    event ShipmentRequest(address indexed shipment);
    
    function packagesWaiting() public view returns (bool)
    {
        return shipments[queue].id != 0;
    }
    
    function dropoff() public payable{
        require(drivers[msg.sender].id == 1, "you're not a driver");
        require(drivers[msg.sender].status == 1, "you're not carrying a package");
        shipments[drivers[msg.sender].package].status = 2;
        drivers[msg.sender].status = 0;
        drivers[msg.sender].loc = shipments[drivers[msg.sender].package].destination;
        msg.sender.transfer(shipments[drivers[msg.sender].package].payment);
    }
    
    function view_contract_balance() public view returns (uint){
        return address(this).balance;
    }
    
    function empty_contract(address payable addr) public payable{
        addr.transfer(address(this).balance);
    }
    
    function getHeadPackage() public view returns (address)
    {
        require(packagesWaiting(), "no packages in queue");
        return queue;
    }
    
    function shipmentExists(address adr) public view returns (bool) {
        return shipments[adr].id == 1;
    }
    
    function claimPackage() public{
        require(drivers[msg.sender].id > 0, "you're not a driver");
        require(drivers[msg.sender].status == 0, "you're already carrying a package");
        require(drivers[msg.sender].available == true, "you're not available");
        require(shipments[queue].status == 0, "package already claimed");
        address curr = queue;
        queue = shipments[queue].nextShipment;
        drivers[msg.sender].status = 1;
        drivers[msg.sender].package = curr;
        drivers[msg.sender].available = false;
        shipments[curr].status = 1;
        shipments[curr].driver = msg.sender;
    }
    
    
    

    // constructor(bytes32 ipfshash) public {
    //     ipfs_hash = ipfshash;
    // }
    
    function get_cost(uint8 origin_lat, uint8 origin_long,uint8 dest_lat, uint8 dest_long) public view returns(uint) {
        uint8 lat_diff = origin_lat - dest_lat;
        uint8 long_diff = origin_long - dest_long;
       uint base_payment = 1000000;
        base_payment = base_payment + (lat_diff*1000000) + (long_diff*1000000);
        return base_payment;
    }
    
    

    function ship_package(uint8 origin_lat, uint8 origin_long,uint8 dest_lat, uint8 dest_long, uint8 weight, uint8 height, uint8 width, uint8 length) public payable{
        require((weight > 0) && (height > 0) && (length > 0) && (width > 0) , "Invalid package dimensions.");
        require(shipments[msg.sender] .weight == 0, "You are already have a package in transit!");
        
        uint8 lat_diff = origin_lat - dest_lat;
        uint8 long_diff = origin_long - dest_long;
        
        uint base_payment = 1000000;
        base_payment = base_payment + (lat_diff*1000000) + (long_diff*1000000);
        require(msg.value >= base_payment, "insufficient funds");

        Location storage origin; 
        origin.lat = origin_lat;
        origin.long = origin_long;
        
        Location storage dest; 
        dest.lat = dest_lat;
        dest.long = dest_long;

        Shipment storage shipment;
        shipment.width = width;
        shipment.height = height;
        shipment.length = length;
        shipment.width = width;
        shipment.id = 1;
        shipment.addr = msg.sender;
        shipment.payment = base_payment;

        //Shipment(width,height, length, weight, origin, dest);
        shipments[msg.sender] = shipment;
        if(packagesWaiting()) {
            shipment.nextShipment = queue;
            queue = msg.sender;
        }
        else {
            queue = msg.sender;
        }
        emit ShipmentRequest(msg.sender);
    }
    
    function unavailable_to_drive() public
    {
        require(drivers[msg.sender].id > 0, "you're not a driver");
        require(drivers[msg.sender].available , "you're not available");
        drivers[msg.sender].available = false;
    }
    
    function driverAvailable(address driver) public view returns (bool)
    {
        require(drivers[driver].weight_capacity > 0, "no such driver");
        return drivers[driver].available;
    }
    
    function driverExists(address driver) public view returns (bool)
    {
        return drivers[driver].weight_capacity > 0;
    }
    
     function get_shipment_status(address adr) public view returns (uint8)
    {
        require(shipments[adr].id == 1, "no shipment");
        return shipments[adr].status;
    }
    
    function get_shipment(address shipment) public view returns(Shipment memory) {
        require(shipments[shipment].id == 1, "no shipment");
        return shipments[shipment];
    }
    
    function get_driver(address driver) public view returns(Driver memory) {
        require(drivers[driver].id > 0, "no driver");
        return drivers[driver];
    }
    
     function get_driver_status(address adr) public view returns (uint8)
    {
        require(drivers[adr].id > 0, "no driver");
        return drivers[adr].status;
    }
    
    function get_package_dest_lat(address package) public view returns (int) {
        require(shipments[package].id == 1, "no such package");
        return shipments[package].destination.lat;
    }
    function get_package_dest_long(address package) public view returns (int) {
        require(shipments[package].id == 1, "no such package");
        return shipments[package].destination.long;
    }
    function get_package_driver(address package) public view returns (address) {
        require(shipments[package].id == 1, "no such package");
        return shipments[package].driver;
    }
    
     function available_to_drive() public
    {
        require(drivers[msg.sender].id > 0, "you're not a driver");
        require(!drivers[msg.sender].available , "you're already available");
        require(drivers[msg.sender].status != 1, "you are carrying a package");
        drivers[msg.sender].available = true;
        emit DriverRequest(msg.sender);
    }
    
    function signup_to_drive(uint8 lat, uint8 long, uint8 weight, uint8 height, uint8 width, uint8 length) public payable{
        require((weight > 0) && (height > 0) && (length > 0) && (width > 0) , "Invalid car dimensions.");
        require(drivers[msg.sender].weight_capacity == 0, "You are already registered to drive!");
        Location storage loc;
        loc.lat = lat;
        loc.long = long;
        Driver storage driver;
        driver.weight_capacity = weight;
        driver.available = false;
        driver.height = height;
        driver.length = length;
        driver.loc = loc;
        driver.id = 1;
        drivers[msg.sender] = driver;
        emit DriverSignup(msg.sender);
    }
    
    function get_driver_package(address adr) public view returns (address) {
        require(drivers[adr].id > 0, "not a driver");
        require(drivers[adr].status == 1, "not carrying");
        return drivers[adr].package;
    }
    function get_driver_goal_long(address adr) public view returns (int) {
        require(drivers[adr].id > 0, "not a driver");
        require(drivers[adr].status == 1, "not carrying");
        return shipments[drivers[adr].package].destination.long;
    }
    function get_driver_goal_lat(address adr) public view returns (int) {
        require(drivers[adr].id > 0, "not a driver");
        require(drivers[adr].status == 1, "not carrying");
        return shipments[drivers[adr].package].destination.lat;
    }
    
}
