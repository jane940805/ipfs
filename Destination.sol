// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "./BridgeToken.sol";

contract Destination is AccessControl {
    bytes32 public constant WARDEN_ROLE = keccak256("BRIDGE_WARDEN_ROLE");
    bytes32 public constant CREATOR_ROLE = keccak256("CREATOR_ROLE");
	mapping( address => address) public underlying_tokens;
	mapping( address => address) public wrapped_tokens;
	address[] public tokens;

	event Creation( address indexed underlying_token, address indexed wrapped_token );
	event Wrap( address indexed underlying_token, address indexed wrapped_token, address indexed to, uint256 amount );
	event Unwrap( address indexed underlying_token, address indexed wrapped_token, address frm, address indexed to, uint256 amount );

    constructor( address admin ) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(CREATOR_ROLE, admin);
        _grantRole(WARDEN_ROLE, admin);
    }

	function wrap(address underlying_token, address recipient, uint256 amount ) public onlyRole(WARDEN_ROLE) {
		//YOUR CODE HERE
		// Ensure the wrapped token is already created
        require(amount > 0, "Cannot mint zero amount");
		require(wrapped_tokens[underlying_token] != address(0), "Wrapped token not created"); 
 
 		// Mint the wrapped tokens to the recipient
        BridgeToken(wrapped_tokens[underlying_token]).mint(recipient, amount); 
        require(recipient != address(0), "Cannot deposit to null account");

		// Emit event
		emit Wrap(underlying_token, wrapped_tokens[underlying_token], recipient, amount);
	}

	function unwrap(address _wrapped_token, address recipient, uint256 amount ) public {
		//YOUR CODE HERE
		// Ensure the wrapped token is valid
        require(amount > 0, "Cannot mint zero amount");
		require(underlying_tokens[_wrapped_token] != address(0), "Wrapped token not created"); 

		// Burn the wrapped tokens
		BridgeToken(_wrapped_token).burnFrom(msg.sender, amount);

		// Transfer the underlying tokens to the recipient
		// ERC20(underlyingToken).transfer(recipient, amount);

		// Emit event
		emit Unwrap(underlying_tokens[_wrapped_token], _wrapped_token, msg.sender, recipient, amount);

	}

	function createToken(address underlying_token, string memory name, string memory symbol ) public onlyRole(CREATOR_ROLE) returns(address) {
		//YOUR CODE HERE
		// Ensure the token doesn't already exist
		require(wrapped_tokens[underlying_token] == address(0), "Wrapped token already exists");

		// Deploy the new BridgeToken contract
		BridgeToken bridgeToken = new BridgeToken(underlying_token, name, symbol, address(this));

		// Map the underlying token to its wrapped token
		wrapped_tokens[underlying_token] = address(bridgeToken);
		underlying_tokens[address(bridgeToken)] = underlying_token;
		tokens.push(address(bridgeToken));
    
		// Emit event
		emit Creation(underlying_token, address(bridgeToken));
		return address(bridgeToken);

	}

}
