import socket
import struct
import time
from datetime import datetime

class NtpSync:
    """
    Handles time synchronization with an NTP server to ensure millisecond precision.
    """
    NTP_SERVER = "pool.ntp.org"
    TIME1970 = 2208988800  # Reference time (1900-01-01 to 1970-01-01)

    def get_ntp_time(self):
        """
        Fetches the current time from an NTP server.

        Returns:
            A datetime object representing the current network time, or None on failure.
        """
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client.settimeout(2) # 2-second timeout
            data = b'\x1b' + 47 * b'\0'
            client.sendto(data, (self.NTP_SERVER, 123))
            data, address = client.recvfrom(1024)
            if data:
                t = struct.unpack('!12I', data)[10]
                t -= self.TIME1970
                return datetime.fromtimestamp(t)
        except (socket.timeout, socket.gaierror) as e:
            print(f"ERROR: Could not connect to NTP server '{self.NTP_SERVER}': {e}")
            return None
        finally:
            client.close()

    def get_time_drift(self):
        """
        Calculates the time difference (drift) between system time and NTP time.

        Returns:
            The time drift in seconds (float), or None on failure.
        """
        ntp_time = self.get_ntp_time()
        if ntp_time:
            system_time = datetime.now()
            drift = (ntp_time - system_time).total_seconds()
            return drift
        return None

if __name__ == '__main__':
    # Test the NTP time synchronization
    ntp_sync = NtpSync()
    print("Attempting to synchronize time with NTP server...")

    ntp_time = ntp_sync.get_ntp_time()
    if ntp_time:
        system_time = datetime.now()
        drift = ntp_sync.get_time_drift()

        print(f"NTP Server Time: {ntp_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
        print(f"System Time:     {system_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
        print(f"Time Drift:      {drift:.4f} seconds")

        if abs(drift) > 1:
            print("\nWARNING: System clock drift is greater than 1 second. Please sync your system time.")
        else:
            print("\nSUCCESS: System clock is synchronized within an acceptable range.")
    else:
        print("\nERROR: Failed to retrieve time from NTP server.")
