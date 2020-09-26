## cwyang's QAT driver RPM package

Thanks for visiting!

While Intel's QAT RPM driver builds kernel module on target machine,
this RPM package delivers pre-built kernel module.

It was my first RPM packaging experience and took a few nights
..
and tons of :coffee: to package QAT driver to RPM.

You can now buy me a coffee! :smile:

<a href="https://www.buymeacoffee.com/cwyang" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 30px !important;width: 108px !important;" ></a>

---
The following data can be specified by `rpmbuild --define "key value"`:
- orgname [RPM build files are located to `/opt/{orgname}`]
- kver    [Kernel version to build driver. Use running kernel if omitted]
- privkey [Kernel module signing private key file. No sign if omited]
- pubkey  [Kernel module signing public key file]

