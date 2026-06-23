import { useRef, useState } from "react";
import useSWR from "swr";
import {
  fetchWards,
  fetchObservations,
  type Ward,
  type Observation,
} from "../api";

const ONE_HOUR = 60 * 60 * 1000;

export function useWeatherData() {
  const [selectedWard, setSelectedWard] = useState<string>("");
  const initialized = useRef(false);

  const {
    data: wards = [],
    isLoading: wardsLoading,
    error: wardsError,
  } = useSWR<Ward[]>("wards", fetchWards, {
    onSuccess: (list) => {
      if (list.length > 0 && !initialized.current) {
        initialized.current = true;
        setSelectedWard(list[0].code);
      }
    },
  });

  const {
    data: observations = [],
    isLoading: loading,
    error: observationsError,
  } = useSWR<Observation[]>(
    selectedWard ? ["observations", selectedWard] : null,
    ([, ward]: [string, string]) => fetchObservations(ward),
    { refreshInterval: ONE_HOUR },
  );

  return {
    wards,
    wardsLoading,
    selectedWard,
    setSelectedWard,
    observations,
    loading,
    errors: {
      wards: wardsError as Error | undefined,
      observations: observationsError as Error | undefined,
    },
  };
}
