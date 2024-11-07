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

function wrap(address underlying token, address  recipient, uint256 amount ) public onlyRole(WARDEN_ROLE) {

address wrappedToken = wrapped_tokens[underlying token];
require(wrappedToken != address(0), "Wrapped token not created");

ERC20 underlyingToken = ERC20(underlying token);
uint256 senderBalance = underlyingToken.balanceOf(msg.sender);
require(senderBalance >= amount, "Insufficient underlying token balance");

bool success = underlyingToken.transferFrom(msg.sender, address(this), amount);
require(success, "Transfer failed");

BridgeToken(wrappedToken).mint(_recipient, amount);

emit Wrap(underlying token, wrappedToken, _recipient, amount);

}

function unwrap(address _wrapped_token, address  recipient, uint256 amount ) public {

address underlyingToken = underlying_tokens[_wrapped_token];
require(underlyingToken != address(0), "Invalid wrapped token");

BridgeToken wrappedToken = BridgeToken(_wrapped_token);
uint256 wrappedTokenBalance = wrappedToken.balanceOf(msg.sender);
require(wrappedTokenBalance >= amount, "Insufficient wrapped token balance");

wrappedToken.burnFrom(msg.sender, amount);

ERC20(underlyingToken).transfer(_recipient, amount);

emit Unwrap(underlyingToken, _wrapped_token, msg.sender, _recipient, amount);

}

function createToken(address underlying token, string memory name, string memory symbol ) public onlyRole(CREATOR_ROLE) returns(address) {

require(wrapped_tokens[underlying token] == address(0), "Wrapped token already exists");


BridgeToken bridgeToken = new BridgeToken(underlying token, name, symbol, msg.sender);

wrapped_tokens[underlying token] = address(bridgeToken);
underlying_tokens[address(bridgeToken)] = underlying token;

emit Creation(underlying token, address(bridgeToken));
return address(bridgeToken);

}

}


