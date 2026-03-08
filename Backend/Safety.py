import os
import re

class SafetyAssessment:
    def __init__(self, tier, requires_confirmation, warning_message, is_allowed=True):
        self.tier = tier
        self.requires_confirmation = requires_confirmation
        self.warning_message = warning_message
        self.is_allowed = is_allowed

class SafetyValidator:
    """
    Gatekeeper validation for Leo AI commands.
    Enforces Authority Tiers and Blacklists.
    """

    TIER_1_SAFE = "SAFE"
    TIER_2_SENSITIVE = "SENSITIVE"
    TIER_3_CRITICAL = "CRITICAL"

    # Keywords for parsing (Simplified from Automation.py)
    VERBS_CRITICAL = ["delete file", "delete", "close", "move file", "rename file", "taskkill"]
    VERBS_SENSITIVE = ["edit file", "write", "create file", "copy file", "save"]
    VERBS_SAFE = ["open", "play", "read file", "list files", "google search", "youtube search", "weather", "file info", "volume", "pause", "resume"]

    # Critical System Paths (Blacklist)
    CRITICAL_PATHS = [
        r"C:\Windows",
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        r"Backend",  # Protect own source code
        r"Main.py",
        r".env"
    ]

    # Critical Processes (Blacklist)
    CRITICAL_APPS = [
        "explorer", "svchost", "csrss", "wininfo", "winlogon", "services", "lsass", "system"
    ]

    @staticmethod
    def _parse_command(cmd):
        """
        Rudimentary parser to extract Verb and Target.
        Must match logic in Automation.py roughly.
        """
        cmd_lower = cmd.lower().strip()
        
        # Exact match / Prefix match logic similar to Automation.py
        all_verbs = SafetyValidator.VERBS_CRITICAL + SafetyValidator.VERBS_SENSITIVE + SafetyValidator.VERBS_SAFE
        
        # Sort by length desc to match longest prefix first (e.g. "delete file" before "delete")
        all_verbs.sort(key=len, reverse=True)
        
        for verb in all_verbs:
            if cmd_lower.startswith(verb):
                target = cmd_lower[len(verb):].strip()
                return verb, target
        
        return "unknown", cmd_lower

    @staticmethod
    def _is_path_safe(path):
        """Check if path targets a blacklisted directory"""
        if not path: return True
        # Normalize path
        norm_path = os.path.normpath(path).lower()
        
        # Check against critical lists
        for bad_path in SafetyValidator.CRITICAL_PATHS:
            bad_path_norm = os.path.normpath(bad_path).lower()
            if bad_path_norm in norm_path:
                return False
        return True

    @staticmethod
    def _is_app_critical(app_name):
        """Check if app name is in critical blacklist"""
        if not app_name: return False
        clean_name = app_name.lower().replace(".exe", "").strip()
        return clean_name in SafetyValidator.CRITICAL_APPS

    @staticmethod
    def analyze_command(command_str):
        """
        Analyze a raw command string and return a SafetyAssessment.
        """
        verb, target = SafetyValidator._parse_command(command_str)
        
        # 1. Check FORBIDDEN (Always Block)
        # --------------------------------
        if verb in ["delete file", "delete", "move file", "rename file"]:
            if not SafetyValidator._is_path_safe(target):
                return SafetyAssessment(
                    tier=SafetyValidator.TIER_3_CRITICAL,
                    requires_confirmation=False,
                    warning_message=f"Action blocked: Usage of restricted system path '{target}' is forbidden.",
                    is_allowed=False
                )

        if verb in ["close", "taskkill"]:
            if SafetyValidator._is_app_critical(target):
                return SafetyAssessment(
                    tier=SafetyValidator.TIER_3_CRITICAL,
                    requires_confirmation=False,
                    warning_message=f"Action blocked: Terminating critical process '{target}' is forbidden.",
                    is_allowed=False
                )

        # 2. Check CRITICAL (Tier 3 - Confirm)
        # -----------------------------------
        if verb in SafetyValidator.VERBS_CRITICAL:
            return SafetyAssessment(
                tier=SafetyValidator.TIER_3_CRITICAL,
                requires_confirmation=True,
                warning_message=f"Warning. You are about to {verb} '{target}'. This action is destructive. Please confirm.",
                is_allowed=True
            )

        # 3. Check SENSITIVE (Tier 2 - Allow but warn/log if needed)
        # ---------------------------------------------------------
        if verb in SafetyValidator.VERBS_SENSITIVE:
            return SafetyAssessment(
                tier=SafetyValidator.TIER_2_SENSITIVE,
                requires_confirmation=False, # Implicit confirmation for now as per contract "Implicit"
                warning_message="",
                is_allowed=True
            )

        # 4. Check SAFE (Tier 1)
        # ---------------------
        return SafetyAssessment(
            tier=SafetyValidator.TIER_1_SAFE,
            requires_confirmation=False,
            warning_message="",
            is_allowed=True
        )
