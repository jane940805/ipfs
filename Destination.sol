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

	function wrap(address _underlying_token, address _recipient, uint256 _amount ) public onlyRole(WARDEN_ROLE) {
		//YOUR CODE HERE
		// Ensure the wrapped token is already created
    require(_amount > 0, "Cannot mint zero amount");
		require(wrapped_tokens[_underlying_token] != address(0), "Wrapped token not created"); // check this line. You can't wrap unregistered token
 
 		// Mint the wrapped tokens to the recipient
		//BridgeToken(wrappedToken).mint(_recipient, _amount);
    BridgeToken(wrapped_tokens[_underlying_token]).mint(_recipient, _amount); 
    require(_recipient != address(0), "Cannot deposit to null account");

		// Emit event
		emit Wrap(_underlying_token, wrapped_tokens[_underlying_token], _recipient, _amount);

	}

	function unwrap(address _wrapped_token, address _recipient, uint256 _amount ) public {
		//YOUR CODE HERE
		// Ensure the wrapped token is valid
    require(_amount > 0, "Cannot mint zero amount");
		require(underlying_tokens[_wrapped_token] != address(0), "Wrapped token not created"); 

		// Burn the wrapped tokens
		BridgeToken(_wrapped_token).burnFrom(msg.sender, _amount);

		// Transfer the underlying tokens to the recipient
		// ERC20(underlyingToken).transfer(_recipient, _amount);

		// Emit event
		emit Unwrap(underlying_tokens[_wrapped_token], _wrapped_token, msg.sender, _recipient, _amount);

	}

	function createToken(address _underlying_token, string memory name, string memory symbol ) public onlyRole(CREATOR_ROLE) returns(address) {
		//YOUR CODE HERE
		// Ensure the token doesn't already exist
		require(wrapped_tokens[_underlying_token] == address(0), "Wrapped token already exists");

		// Deploy the new BridgeToken contract
		BridgeToken bridgeToken = new BridgeToken(_underlying_token, name, symbol, address(this));

		// Map the underlying token to its wrapped token
		wrapped_tokens[_underlying_token] = address(bridgeToken);
		underlying_tokens[address(bridgeToken)] = _underlying_token;
		tokens.push(address(bridgeToken));
    
		// Emit event
		emit Creation(_underlying_token, address(bridgeToken));
		return address(bridgeToken);

	}

}