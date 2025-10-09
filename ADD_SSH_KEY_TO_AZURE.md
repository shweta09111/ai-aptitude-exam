# Add SSH Key to Azure VM

## Your SSH Public Key
Copy this entire key (it's one long line):

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC5gJJodkJYhax1vUJvElcryneOAzag5BtXabR3SojhZDCJOqkk/b+Ze0lj9frtutmaAWM5d597yOuHR9svarNtOcS4l1Ep0eTXHONO8IKpRbYpxv8ZPMqOoU1A3OZyoUqdBCpVp7ELIBM/J2you7ckuqdyefGdY4YA13DMJ2OPNS0H5mUroJZn7BOPjQQ9ZKoA9Y0/NdRDDN0xTwWMZrtf7SCKEnJs+afuwCsDSGRJYkhHW2RIvwTNSag8KG7DbHBM4UoxZ0ObOYEiJwqAVFwEetzwbZN8NWOIAsIeYQqaJIecqI/hPrP4BiYCxUE9TiPwgGTvVTtuY8pwyQnWkh77A4DpPaOJnLa73ZVT9TBpS4BgFHNHADCKVDKzpSIiXsQi1+cYhrYNMnrjsgP3L7IWgXgWyoIhsI5Sff7T4powLRwTyB4Ug6lINfDIJUShGkFTPOZbE4olwnFEObxvzDKWRP2apE4LYY7jvS63QK+BbkCWbB3PgDGUOTiG/1OS3481T88nlbUvX3IZwGklMRbEMG+aViF0KMpY0vHHXYVyIQjBzccfwRP14wvzTjFiDWiy1HNpg4Gx7dD5GzI/B74GSSQ2tuD5fGAT4pmwVEz5zl+RYM4nzGlmkKV+06ANPTF82qBbXPFIIO/IOgfhl5BdUiNxugCEagX+qGR0CCaIIw== admin@DESKTOP-9P51GKI
```

## Method 1: Add SSH Key via Azure Portal (Easiest)

### Option A: Reset Password to Enable SSH Key
1. Go to Azure Portal: https://portal.azure.com
2. Navigate to your VM: **ai-aptitude-exam**
3. Click **"Reset password"** in the left menu (under Operations/Help)
4. Select **"Reset SSH public key"** or **"Reset password"** mode
5. Enter:
   - Username: `azureuser`
   - SSH public key: Paste the key above
6. Click **"Update"**
7. Wait 2-3 minutes for the changes to apply

### Option B: Use Azure Cloud Shell
1. Go to Azure Portal
2. Click the Cloud Shell icon (>_) in the top toolbar
3. Choose **Bash**
4. Run these commands:

```bash
# Get your VM details
az vm show --resource-group ai-exam-rg --name ai-aptitude-exam

# Add your SSH key
az vm user update \
  --resource-group ai-exam-rg \
  --name ai-aptitude-exam \
  --username azureuser \
  --ssh-key-value "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC5gJJodkJYhax1vUJvElcryneOAzag5BtXabR3SojhZDCJOqkk/b+Ze0lj9frtutmaAWM5d597yOuHR9svarNtOcS4l1Ep0eTXHONO8IKpRbYpxv8ZPMqOoU1A3OZyoUqdBCpVp7ELIBM/J2you7ckuqdyefGdY4YA13DMJ2OPNS0H5mUroJZn7BOPjQQ9ZKoA9Y0/NdRDDN0xTwWMZrtf7SCKEnJs+afuwCsDSGRJYkhHW2RIvwTNSag8KG7DbHBM4UoxZ0ObOYEiJwqAVFwEetzwbZN8NWOIAsIeYQqaJIecqI/hPrP4BiYCxUE9TiPwgGTvVTtuY8pwyQnWkh77A4DpPaOJnLa73ZVT9TBpS4BgFHNHADCKVDKzpSIiXsQi1+cYhrYNMnrjsgP3L7IWgXgWyoIhsI5Sff7T4powLRwTyB4Ug6lINfDIJUShGkFTPOZbE4olwnFEObxvzDKWRP2apE4LYY7jvS63QK+BbkCWbB3PgDGUOTiG/1OS3481T88nlbUvX3IZwGklMRbEMG+aViF0KMpY0vHHXYVyIQjBzccfwRP14wvzTjFiDWiy1HNpg4Gx7dD5GzI/B74GSSQ2tuD5fGAT4pmwVEz5zl+RYM4nzGlmkKV+06ANPTF82qBbXPFIIO/IOgfhl5BdUiNxugCEagX+qGR0CCaIIw== admin@DESKTOP-9P51GKI"
```

## Method 2: Use Azure CLI (If installed locally)

```powershell
# Install Azure CLI if not already installed
# winget install -e --id Microsoft.AzureCLI

# Login to Azure
az login

# Add SSH key to VM
az vm user update \
  --resource-group ai-exam-rg \
  --name ai-aptitude-exam \
  --username azureuser \
  --ssh-key-value "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC5gJJodkJYhax1vUJvElcryneOAzag5BtXabR3SojhZDCJOqkk/b+Ze0lj9frtutmaAWM5d597yOuHR9svarNtOcS4l1Ep0eTXHONO8IKpRbYpxv8ZPMqOoU1A3OZyoUqdBCpVp7ELIBM/J2you7ckuqdyefGdY4YA13DMJ2OPNS0H5mUroJZn7BOPjQQ9ZKoA9Y0/NdRDDN0xTwWMZrtf7SCKEnJs+afuwCsDSGRJYkhHW2RIvwTNSag8KG7DbHBM4UoxZ0ObOYEiJwqAVFwEetzwbZN8NWOIAsIeYQqaJIecqI/hPrP4BiYCxUE9TiPwgGTvVTtuY8pwyQnWkh77A4DpPaOJnLa73ZVT9TBpS4BgFHNHADCKVDKzpSIiXsQi1+cYhrYNMnrjsgP3L7IWgXgWyoIhsI5Sff7T4powLRwTyB4Ug6lINfDIJUShGkFTPOZbE4olwnFEObxvzDKWRP2apE4LYY7jvS63QK+BbkCWbB3PgDGUOTiG/1OS3481T88nlbUvX3IZwGklMRbEMG+aViF0KMpY0vHHXYVyIQjBzccfwRP14wvzTjFiDWiy1HNpg4Gx7dD5GzI/B74GSSQ2tuD5fGAT4pmwVEz5zl+RYM4nzGlmkKV+06ANPTF82qBbXPFIIO/IOgfhl5BdUiNxugCEagX+qGR0CCaIIw== admin@DESKTOP-9P51GKI"
```

## After Adding the SSH Key

Wait 2-3 minutes, then try connecting again:

```powershell
ssh azureuser@20.40.44.73
```

If it asks "Are you sure you want to continue connecting?", type `yes` and press Enter.

## VM Details
- **VM Name**: ai-aptitude-exam
- **Resource Group**: ai-exam-rg (or check your Azure Portal)
- **Public IP**: 20.40.44.73
- **Username**: azureuser
- **SSH Key Location**: C:\Users\Admin\.ssh\id_rsa (private key)
- **SSH Public Key Location**: C:\Users\Admin\.ssh\id_rsa.pub

## Alternative: Enable Password Authentication (Less Secure)

If you prefer password authentication, you'll need to:
1. SSH into the VM using another method (Azure Serial Console)
2. Edit `/etc/ssh/sshd_config`
3. Set `PasswordAuthentication yes`
4. Restart SSH: `sudo systemctl restart sshd`
5. Set a password: `sudo passwd azureuser`

**Recommended**: Use SSH key authentication (Method 1 or 2 above) for better security.

## Next Steps After Successful SSH

Once you can SSH into the VM, follow the deployment guide:
1. Install required packages (Python, pip, git, nginx, etc.)
2. Clone your GitHub repository
3. Set up the application
4. Configure systemd service
5. Set up Nginx reverse proxy
6. Configure firewall for HTTP/HTTPS

Refer to `DEPLOY_TO_AZURE_NOW.md` for detailed deployment steps.
