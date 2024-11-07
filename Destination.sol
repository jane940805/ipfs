// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "./BridgeToken.sol";

contract Destination is AccessControl {
    bytes32 public constant WARDEN_ROLE = keccak256("BRIDGE_WARDEN_ROLE");
    bytes32 public constant CREATOR_ROLE = keccak256("CREATOR_ROLE");
    
    // Mapping from underlying token addresses to their respective bridge-wrapped tokens
    mapping(address => address) public underlying_tokens;
    mapping(address => address) public wrapped_tokens;
    address[] public tokens;

    // Events for contract actions
    event Creation(address indexed underlying_token, address indexed wrapped_token);
    event Wrap(address indexed underlying_token, address indexed wrapped_token, address indexed to, uint256 amount);
    event Unwrap(address indexed underlying_token, address indexed wrapped_token, address frm, address indexed to, uint256 amount);

    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(CREATOR_ROLE, admin);
        _grantRole(WARDEN_ROLE, admin);
    }

    // Function to create a new wrapped token for a specific underlying asset
    function createToken(address _underlying_token, string memory name, string memory symbol) 
        public onlyRole(CREATOR_ROLE) 
        returns (address) 
    {
        require(underlying_tokens[_underlying_token] == address(0), "Token already created");

        // Deploy a new BridgeToken
        BridgeToken newWrappedToken = new BridgeToken(name, symbol, _underlying_token);
        
        // Map the underlying token to the newly created wrapped token
        address wrappedTokenAddress = address(newWrappedToken);
        underlying_tokens[_underlying_token] = wrappedTokenAddress;
        wrapped_tokens[wrappedTokenAddress] = _underlying_token;
        tokens.push(_underlying_token);

        emit Creation(_underlying_token, wrappedTokenAddress);
        return wrappedTokenAddress;
    }

    // Function to wrap tokens: mints wrapped tokens for the recipient
    function wrap(address _underlying_token, address _recipient, uint256 _amount) 
        public onlyRole(WARDEN_ROLE) 
    {
        address wrappedTokenAddr = underlying_tokens[_underlying_token];
        require(wrappedTokenAddr != address(0), "Token not registered");

        // Mint bridge tokens to the recipient
        BridgeToken(wrappedTokenAddr).mint(_recipient, _amount);

        emit Wrap(_underlying_token, wrappedTokenAddr, _recipient, _amount);
    }

    // Function to unwrap tokens: burns wrapped tokens and logs the unwrapping
    function unwrap(address _wrapped_token, address _recipient, uint256 _amount) public {
        address underlyingTokenAddr = wrapped_tokens[_wrapped_token];
        require(underlyingTokenAddr != address(0), "Invalid wrapped token");

        // Verify the caller owns enough tokens
        BridgeToken wrappedToken = BridgeToken(_wrapped_token);
        require(wrappedToken.balanceOf(msg.sender) >= _amount, "Insufficient balance to unwrap");

        // Burn the specified amount from the caller
        wrappedToken.burn(msg.sender, _amount);

        emit Unwrap(underlyingTokenAddr, _wrapped_token, msg.sender, _recipient, _amount);
    }
}
