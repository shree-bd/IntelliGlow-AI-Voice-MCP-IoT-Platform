# 💡 IntelliGlow - AI-Powered Smart Lighting

**"Smart lighting, brilliantly simple"**

IntelliGlow is a Model Context Protocol (MCP) server that allows AI assistants like Claude and ChatGPT to control **real smart bulbs** via UDP network communication. This Python implementation features voice commands, AI reasoning, and direct hardware control.

## 🏗️ **Architecture**

```
Voice/AI ──> IntelliGlow MCP ──> UDP Network ──> Smart Bulb (192.168.1.45:4000)
```

**The smart bulb system that actually thinks!!**

## 🌟 **Features**

### **🔴 Real Hardware Support** 
- **UDP Network Communication**: Direct communication with real smart bulbs
- **Default Bulb Configuration**: Connects to `192.168.1.45:4000` by default
- **Network Discovery**: Automatically find smart bulbs on your network
- **Connection Management**: Persistent connections with auto-reconnect

### **🎤 Voice Intelligence**
- **Natural Voice Commands**: "Turn on lights", "Set brightness to 75", "Make it blue"
- **AI-Powered Parsing**: Understands context and natural language
- **Text-to-Speech Feedback**: Speaks responses back to you
- **Smart Color Recognition**: Recognizes color names and descriptive terms

### **🧠 AI Integration**
- **MCP Protocol**: Works with Claude, GPT, and other AI models
- **Context Understanding**: AI can reason about lighting needs
- **Workflow Integration**: Bulbs become part of larger AI workflows
- **Learning Capability**: Can adapt to user patterns and preferences

### **🔧 Smart Bulb Control**
- **Power Control**: Turn bulbs on/off via UDP commands
- **Brightness Control**: Adjust brightness levels (0-100%)
- **Color Control**: Full RGB control with hex color codes (#FF0000)
- **Status Monitoring**: Get real-time bulb status
- **Ping/Connectivity**: Test network connectivity to bulbs

### **🌐 Network Features**
- **Multi-bulb Support**: Connect to multiple bulbs simultaneously
- **Discovery**: Scan network for available smart bulbs
- **Environment Configuration**: Set bulb IP/port via environment variables

## 🚀 **Quick Start**

### **Installation**

1. **Install IntelliGlow**:
   ```bash
   # Core system
   pip install -e .
   
   # With voice capabilities
   pip install -e .[voice]
   ```

2. **Configure your bulb** (optional):
   ```bash
   export BULB_IP=192.168.1.45    # Your bulb's IP
   export BULB_PORT=4000          # Your bulb's port
   ```

### **Running IntelliGlow**

```bash
# 1. MCP server only (for AI integration)
mcp-server-smartbulb

# 2. Voice interface only
mcp-server-smartbulb-voice

# 3. Complete IntelliGlow system (voice + AI + MCP)
python voice_enabled_server.py
```

### **Testing Network Connectivity**

```bash
# Test UDP communication with your real bulb
python test_network_bulbs.py
```

## 🔧 **AI Integration (Claude Desktop)**

Add this to your Claude Desktop `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "intelliglow": {
      "command": "python",
      "args": ["-m", "mcp_server_smartbulb.network_server"],
      "cwd": "/path/to/your/IntelliGlow",
      "env": {
        "BULB_IP": "192.168.1.45",
        "BULB_PORT": "4000"
      }
    }
  }
}
```

## 🛠️ **Available Commands**

### **🎤 Voice Commands**
- *"Turn on the lights"* - Power control
- *"Set brightness to 75 percent"* - Brightness with smart parsing
- *"Make it blue"* - Color recognition
- *"How are the lights?"* - Status inquiry
- *"Find smart bulbs"* - Network discovery

### **🤖 MCP Tools (for AI)**
- `discover_bulbs()` - Find smart bulbs on the network
- `connect_to_bulb(ip, port)` - Connect to a specific bulb
- `turn_on_bulb(ip, port)` - Turn on a bulb via UDP
- `turn_off_bulb(ip, port)` - Turn off a bulb via UDP
- `set_bulb_brightness(brightness, ip, port)` - Set brightness (0-100)
- `set_bulb_color(color, ip, port)` - Set color using hex codes
- `get_bulb_status(ip, port)` - Get current bulb status
- `ping_bulb(ip, port)` - Test connectivity to a bulb

## 📡 **Network Configuration**

### **Default Bulb Setup**
IntelliGlow connects to `192.168.1.45:4000` by default. You can override this:

```bash
export BULB_IP=192.168.1.100
export BULB_PORT=4001
```

### **Bulb Configuration File**
Create `bulb_config.json`:
```json
{
  "default_bulb": {
    "ip": "192.168.1.45",
    "port": 4000,
    "timeout": 5.0
  },
  "discovery": {
    "enabled": true,
    "timeout": 10.0,
    "port_range": {
      "start": 4000,
      "end": 4010
    }
  }
}
```

## 🔍 **IntelliGlow vs Traditional Solutions**

| Feature | **Alexa/Google** | **IntelliGlow** |
|---------|------------------|-----------------|
| **Voice Control** | ✅ Basic commands | ✅ Natural language + AI reasoning |
| **AI Integration** | ❌ Limited ecosystem | ✅ Works with any AI model (Claude, GPT, etc.) |
| **Hardware Control** | ❌ Cloud-dependent | ✅ Direct UDP networking |
| **Customization** | ❌ Vendor limitations | ✅ Full control over protocol |
| **Context Understanding** | ❌ Simple keywords | ✅ AI understands context and workflows |
| **Privacy** | ❌ Cloud processing | ✅ Local processing |
| **Developer Freedom** | ❌ Closed ecosystem | ✅ Open protocol, extensible |

**Result**: IntelliGlow = Convenience of Alexa + Intelligence of AI + Freedom of Open Source! 🎉

## 🧪 **Testing**

```bash
# Test real UDP communication with your bulb
python test_network_bulbs.py
```

This will:
1. 🔌 Test direct connection to 192.168.1.45:4000
2. 🔍 Scan network for other bulbs  
3. 🤖 Simulate AI/MCP commands
4. 🎤 Test voice command processing

## 🐛 **Troubleshooting**

### **No Bulb Found**
- Ensure your smart bulb is on the same network
- Check that the bulb is listening on port 4000
- Try network discovery: `python -c "import asyncio; from mcp_server_smartbulb.bulb_discovery import BulbDiscovery; asyncio.run(BulbDiscovery().discover_bulbs())"`

### **Voice Not Working**
- Install voice dependencies: `pip install -e .[voice]`
- Check microphone permissions
- Test with: `python -m mcp_server_smartbulb.voice_interface`

### **Connection Timeout**
- Check firewall settings
- Verify bulb IP address
- Increase timeout in `bulb_config.json`

## 📁 **Project Structure**

```
IntelliGlow/
├── mcp_server_smartbulb/
│   ├── __init__.py              # Package initialization 
│   ├── network_server.py        # Main UDP-enabled MCP server
│   ├── udp_client.py           # UDP networking client
│   ├── bulb_discovery.py       # Network discovery
│   └── voice_interface.py      # Voice command processing
├── bulb_config.json            # Network configuration
├── test_network_bulbs.py       # UDP testing script
├── voice_enabled_server.py     # Complete IntelliGlow system
├── README.md                   # This file
└── pyproject.toml              # Project configuration
```

**Clean, focused, and intelligent! 🧠💡**

## 🎯 **What Makes IntelliGlow Special**

**IntelliGlow isn't just another smart bulb controller - it's the bridge between AI intelligence and physical hardware.**

### **🔥 Key Innovations:**
- **AI-Native Design**: Built for AI reasoning, not just voice commands
- **Open Protocol**: Works with any AI model, not locked to one vendor
- **Local Processing**: Privacy-focused, no cloud dependency required
- **Hybrid Interface**: Voice + AI chat + MCP protocol
- **Developer Freedom**: Full customization and extensibility

### **🌟 Real-World Magic:**
```
User: "I'm working late and need focus lighting"
IntelliGlow: 
→ AI understands context
→ Sets cool white light (5000K)
→ Optimal brightness (85%)
→ Direct UDP communication
→ Responds with confirmation
```

**This is the future of smart homes - lighting that truly understands and adapts to your needs!** 🚀

---

**Made with ❤️ for the next generation of intelligent home automation** 
