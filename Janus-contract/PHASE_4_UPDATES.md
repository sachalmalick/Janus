So most of the phase 4 changes will become apparent when I finish my IPFS integration as I am moving a ton of on-chain data, off-chain, to reduce block size and gas fees.

-I will be hashing a users password and appending it to their address for uniqueness and using that to reference off chain data from IPFS, so that will become their unique identifer.  That way, there's nothing on chain that can be used to access that user's data in IPFS.

-I have already been emitting events since Phase 3.

-I added a password requirement for the driver signup, which I hash using keccak256 and store in an on-chain mapping.

-I added a modifier for authenticating drivers using their password.

-I added a test driver function which would allow them to view their current car's weight capacity and added a password requirement for this function.
	-In the web application version I will be storing passwords in a session so they don't have to renter for each transaction.
	
